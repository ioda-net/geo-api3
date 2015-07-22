import decimal
import datetime


from pyramid.view import view_config
import pyramid.httpexceptions as exc

from chsdi.lib.validation.mapservice import MapServiceValidation
from chsdi.models import models_from_name

SAMPLE_SIZE = 100
MAX_ATTRIBUTES_VALUES = 5


class LayersParams(MapServiceValidation):

    def __init__(self, request):
        super(LayersParams, self).__init__()

        # Map and topic represent the same resource
        self.mapName = request.matchdict.get('map')
        self.cbName = request.params.get('callback')
        self.lang = request.lang
        self.searchText = request.params.get('searchText')
        # Not to be published in doc
        self.chargeable = request.params.get('chargeable')

        self.translate = request.translate
        self.request = request


def _find_type(model, colProp):
    if hasattr(model, '__table__') and hasattr(model, colProp):
        return model.get_column_by_property_name(colProp).type


def _get_models_attributes_keys(models, lang):
    allAttributes = []
    for model in models:
        if hasattr(model, '__queryable_attributes__'):
            attributes = model.get_queryable_attributes_keys(lang)
        else:
            # Maybe this should be removed since only searchable layers
            # have attributes that can be queried
            attributes = model().getAttributesKeys()
        allAttributes = allAttributes + attributes
    return list(set(allAttributes))


# Could be moved in features.py as it accesses vector models
@view_config(route_name='featureAttributes', renderer='jsonp')
def feature_attributes(request):
    ''' This service is used to expose the
    attributes of vector layers. '''
    params = LayersParams(request)
    layerId = request.matchdict.get('layerId')
    models = models_from_name(layerId)
    # Models for the same layer have the same attributes
    if models is None:
        raise exc.HTTPBadRequest('No Vector Table was found for %s' % layerId)

    # Take into account all models and remove duplicated keys
    attributes = _get_models_attributes_keys(models, params.lang)
    trackAttributesNames = []
    fields = []

    def insertValueAt(field, attrName, value):
        if field['name'] == attrName:
            if len(field['values']) < MAX_ATTRIBUTES_VALUES and \
               value not in field['values']:
                field['values'].append(value)
                field['values'].sort()
        return field

    for model in models:
        query = params.request.db.query(model)
        query = query.limit(SAMPLE_SIZE)

        for rowIndex, row in enumerate(query):
            # attrName as defined in the model
            for attrIndex, attrName in enumerate(attributes):
                featureAttrs = row.getAttributes(excludePkey=False)
                if attrName not in trackAttributesNames and \
                   attrName in featureAttrs:
                    fieldType = _find_type(model(), attrName)
                    fields.append({'name': attrName, 'type': str(fieldType),
                                   'alias': params.translate("%s.%s" % (layerId, attrName)),
                                   'values': []
                                   })
                    trackAttributesNames.append(attrName)
                if attrName in featureAttrs:
                    for fieldsIndex, field in enumerate(fields):
                        value = featureAttrs[attrName]
                        if isinstance(value, (decimal.Decimal, datetime.date, datetime.datetime)):
                            value = str(value)
                        fields[fieldsIndex] = insertValueAt(field, attrName, value)

    return {'id': layerId, 'name': params.translate(layerId), 'fields': fields}


def _filter_on_chargeable_attr(params, query, model):
    ''' Filter on chargeable parameter '''
    if params.chargeable is not None:
        return query.filter(model.chargeable == params.chargeable)
    return query
