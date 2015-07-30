import re

from pyramid.view import view_config
import pyramid.httpexceptions as exc

from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from sqlalchemy.exc import InternalError
from sqlalchemy.sql.expression import cast
from sqlalchemy import Text, Integer, Boolean, Numeric, Date
from sqlalchemy import text
from geoalchemy2.types import Geometry

from chsdi.models import feature_model_from_name
from chsdi.lib.helpers import format_query
from chsdi.lib.filters import full_text_search
from chsdi.lib.validation.mapservice import MapServiceValidation


# For several features
class FeatureParams(MapServiceValidation):

    def __init__(self, request):
        super().__init__()
        # Map and topic represent the same resource
        self.portal_name = request.matchdict.get('portal')
        self.cbName = request.params.get('callback')
        self.returnGeometry = request.params.get('returnGeometry')
        self.request = request
        self.varnish_authorized = request.headers\
            .get('X-SearchServer-Authorized', 'false')\
            .lower() == 'true'

# for releases requests


def _get_features_params(request):
    params = FeatureParams(request)
    # where must come first order matters, see MapServiceValidation
    params.where = request.params.get('where')
    params.searchText = request.params.get('searchText')
    params.geometry = request.params.get('geometry')
    params.geometryType = request.params.get('geometryType')
    params.imageDisplay = request.params.get('imageDisplay')
    params.mapExtent = request.params.get('mapExtent')
    params.tolerance = request.params.get('tolerance')
    params.layers = request.params.get('layers', 'all')
    params.offset = request.params.get('offset')
    return params


# For feature, htmlPopup and extendedHtmlPopup services
def _get_feature_params(request):
    params = FeatureParams(request)
    params.layerId = request.matchdict.get('layerId')
    params.featureIds = request.matchdict.get('featureId')
    return params


def _get_find_params(request):
    params = FeatureParams(request)
    params.layer = request.params.get('layer')
    params.searchText = request.params.get('searchText')
    params.searchField = request.params.get('searchField')
    params.contains = request.params.get('contains')
    return params


@view_config(route_name='identify', renderer='geojson', request_param='geometryFormat=geojson')
def identify_geojson(request):
    return _identify(request)


@view_config(route_name='feature', renderer='geojson',
             request_param='geometryFormat=geojson')
def view_get_feature_geojson(request):
    return _get_feature_service(request)


@view_config(route_name='feature', renderer='esrijson')
def view_get_feature_esrijson(request):
    return _get_feature_service(request)


# order matters, last route is the default one!
@view_config(route_name='find', renderer='geojson',
             request_param='geometryFormat=geojson')
def view_find_geojson(request):
    return _find(request)


@view_config(route_name='find', renderer='esrijson')
def view_find_esrijson(request):
    return _find(request)


def _identify(request):
    params = _get_features_params(request)

    layerIds = params.layers
    models = [
        feature_model_from_name(params.portal_name, layerId) for
        layerId in layerIds
        if feature_model_from_name(params.portal_name, layerId) is not None
    ]
    if models is None or len(models) == 0:
        raise exc.HTTPBadRequest('No GeoTable was found for %s' % ' '.join(layerIds))

    maxFeatures = 201
    features = []
    feature_gen = _get_features_for_filters(params, models, maxFeatures=maxFeatures, where=params.where)
    while True:
        try:
            feature = next(feature_gen)
        except InternalError as e:  # pragma: no cover
            raise exc.HTTPBadRequest('Your request generated the following database error: %s' % e)
        except StopIteration:
            break
        else:
            f = _process_feature(feature, params)
            features.append(f)

            if len(features) > maxFeatures:  # pragma: no cover
                break

    return {'results': features}


def _get_feature_service(request):
    params = _get_feature_params(request)
    features = []
    for feature, vectorModel in _get_features(params):
        features.append(feature)
    if len(features) == 1:
        return features[0]
    return features


def _get_features(params, extended=False):
    ''' Returns exactly one feature or raises
    an excpetion '''
    featureIds = params.featureIds.split(',')
    models = feature_model_from_name(params.portal_name, params.layerId)
    if models is None:
        raise exc.HTTPBadRequest('No Vector Table was found for %s' % params.layerId)

    for featureId in featureIds:
        # One layer can have several models
        for model in models:
            query = params.request.db.query(model)
            query = query.filter(model.id == featureId)
            try:
                feature = query.one()
            except NoResultFound:
                feature = None
            except MultipleResultsFound:  # pragma: no cover
                raise exc.HTTPInternalServerError('Multiple features found for the same id %s' % featureId)

            if feature is not None:
                vectorModel = model
                break

        if feature is None:
            raise exc.HTTPNotFound('No feature with id %s' % featureId)
        feature = _process_feature(feature, params)
        feature = {'feature': feature}
        yield feature, vectorModel


def _get_features_for_filters(params, models, maxFeatures=None, where=None):
    ''' Returns a generator function that yields
    a feature. '''
    for vectorLayer in models:
        for model in vectorLayer:
            query = params.request.db.query(model)

            # Filter by sql query
            # Only one filter = one layer
            if where is not None:
                txt = format_query(model, where)
                if txt is None:
                    raise exc.HTTPBadRequest('The where clause is not valid.')
                query = query.filter(text(
                    txt
                ))
            # Filter by bbox
            if params.geometry is not None:
                geomFilter = model.geom_filter(
                    params.geometry,
                    params.geometryType,
                    params.imageDisplay,
                    params.mapExtent,
                    params.tolerance
                )
                # Can be None because of max and min scale
                if geomFilter is not None:
                    # TODO Remove code specific clauses
                    query = query.order_by(model.bgdi_order) if hasattr(model, 'bgdi_order') else query
                    query = query.filter(geomFilter)

            # Add limit
            query = query.limit(maxFeatures) if maxFeatures is not None else query

            # Add offset
            if params.offset is not None:
                query = query.offset(params.offset)

            # We need either where or geomFilter (geomFilter especially for zeitreihen layer)
            # This probably needs refactoring...
            if where is not None or geomFilter is not None:
                for feature in query:
                    yield feature


def _find(request):
    MaxFeatures = 50
    params = _get_find_params(request)
    if params.searchText is None:
        raise exc.HTTPBadRequest('Please provide a searchText')

    models = feature_model_from_name(params.portal_name, params.layer)
    features = []
    findColumn = lambda x: (x, x.get_column_by_property_name(params.searchField))
    if models is None:
        raise exc.HTTPBadRequest('No Vector Table was found for %s' % params.layer)
    for model in models:
        vectorModel, searchColumn = findColumn(model)
        if searchColumn is None:
            raise exc.HTTPBadRequest('Please provide an existing searchField')
        query = request.db.query(vectorModel)
        if params.contains:
            query = full_text_search(
                query,
                [searchColumn],
                params.searchText
            )
        else:
            if isinstance(searchColumn.type, Date):
                query = query.filter(
                    cast(searchColumn, Date) == params.searchText
                )
            else:
                searchText = _format_search_text(searchColumn.type, params.searchText)
                query = query.filter(
                    searchColumn == searchText
                )
        query = query.limit(MaxFeatures)
        for feature in query:
            f = _process_feature(feature, params)
            features.append(f)

    return {'results': features}


def _format_search_text(columnType, searchText):
    if isinstance(columnType, Text):
        return searchText
    elif isinstance(columnType, Boolean):
        if searchText.lower() == 'true':
            return True
        elif searchText.lower() == 'false':
            return False
        else:
            raise exc.HTTPBadRequest('Please provide a boolean value (true/false)')
    elif isinstance(columnType, Integer):
        if searchText.isdigit():
            return int(searchText)
        else:
            raise exc.HTTPBadRequest('Please provide an integer')
    elif isinstance(columnType, Numeric):
        if re.match('^\d+?\.\d+?$', searchText) is not None:
            return float(searchText)
        else:
            raise exc.HTTPBadRequest('Please provide a float')
    elif isinstance(columnType, Geometry):
        raise exc.HTTPBadRequest('Find operations cannot be performed on geometry columns')


def _process_feature(feature, params):
    if params.returnGeometry:
        f = feature.__geo_interface__
    else:
        f = feature.__interface__
    if hasattr(f, 'extra'):
        layerBodId = f.extra['layerBodId']
        f.extra['layerName'] = layerBodId
    else:
        layerBodId = f.get('layerBodId')
        f['layerName'] = layerBodId
    return f
