import decimal
import datetime
from operator import add

import geojson
import json
from geojson.codec import GeoJSONEncoder

from papyrus.geo_interface import GeoInterface
from geojson.crs import Named
from functools import reduce

from chsdi.lib.helpers import float_raise_nan


class EsriGeoJSONEncoder(GeoJSONEncoder):

    srs = 21781

    def _cleanup(self, ret):
        if 'coordinates' in ret:
            del ret['coordinates']
        if 'type' in ret:
            del ret['type']

        if 'properties' in ret:
            if len(ret['properties']) > 0:
                if 'attributes' not in ret:
                    ret['attributes'] = {}
                ret['attributes'].update(ret['properties'])
            del ret['properties']
        if 'crs' in ret:
            crs = ret['crs']
            if crs['type'] == 'name':
                pass
        else:
            ret['spatialReference'] = {'wkid': self.srs}
        return ret

    def default(self, obj):
        geom_type = None
        if hasattr(obj, '__geo_interface__'):
            geom_type = dict(obj.__geo_interface__)['type']

        if isinstance(obj, (decimal.Decimal, datetime.date, datetime.datetime)):
            return str(obj)

        if isinstance(obj, GeoInterface):
            self.srs = obj.geometry_column().type.srid
            obj = obj.__geo_interface__

        if isinstance(obj, (geojson.GeoJSON)):
            ret = dict(obj)
            if 'coordinates' in ret:
                coordinates = ret['coordinates']

            if isinstance(obj, (geojson.Feature, geojson.feature.Feature)) or \
                    geom_type == 'Feature':
                ret = dict(obj)
                geometry = self.default(obj.geometry)
                ret = dict(obj)
                ret['geometry'] = geometry
                esriType = 'esriGeometryPoint'
                if 'rings' in geometry:
                    esriType = 'esriGeometryPolygon'
                if 'paths' in geometry:
                    esriType = 'esriGeometryPolyline'
                ret['geometryType'] = esriType

                return self._cleanup(ret)

            if isinstance(obj, (geojson.FeatureCollection)):
                features = []
                for feature in obj.features:
                    features.append(self.default(feature))

                ret = dict(obj)
                ret['features'] = features
                return self._cleanup(ret)

            if isinstance(obj, (geojson.Point)):
                ret = dict(obj)

                ret['x'], ret['y'] = coordinates
                ret['type'] = 'esriGeometryPoint'

                return self._cleanup(ret)

            if isinstance(obj, geojson.geometry.LineString):
                ret = dict(obj)

                path = coordinates  # ret['coordinates']
                mapPointList = (lambda s, x, y: (x, y))
                ret['paths'] = [[mapPointList(self.srs, *xy) for xy in path]]
                ret['type'] = 'esriGeometryPolyline'

                return self._cleanup(ret)

            if isinstance(obj, (geojson.MultiPoint)):
                ret = dict(obj)
                mapPointList = (lambda s, x, y: (x, y))
                points = [mapPointList(self.srs, *xy) for xy in coordinates]
                ret['points'] = points
                ret['type'] = 'esriGeometryMultipoint'

                return self._cleanup(ret)

            if isinstance(obj, geojson.MultiLineString):
                ret = dict(obj)

                paths = coordinates
                mapPointList = (lambda s, x, y: (x, y))
                ret['paths'] = [[mapPointList(self.srs, *xy) for xy in p] for p in paths]
                ret['type'] = 'esriGeometryPolyline'

                return self._cleanup(ret)

            if isinstance(obj, (geojson.Polygon, geojson.geometry.Polygon)) or \
                    geom_type == 'Polygon':
                ret = dict(obj)

                rings = coordinates
                mapPointList = (lambda s, x, y: (x, y))
                ret['rings'] = [[mapPointList(self.srs, *xy) for xy in ring] for ring in rings]
                ret['type'] = 'esriGeometryPolygon'

                return self._cleanup(ret)

            if isinstance(obj, geojson.MultiPolygon):
                ret = dict(obj)

                mapPointList = (lambda s, x, y: (x, y))
                rings = reduce(add, coordinates)
                ret['rings'] = [[mapPointList(self.srs, *xy) for xy in ring] for ring in rings]
                ret['type'] = 'esriGeometryPolygon'

                return self._cleanup(ret)
        return GeoJSONEncoder.default(self, obj)


class EsriSimple():

    @classmethod
    def to_instance(cls, ob, default=None, strict=False):
        if isinstance(ob, list):
            coords = ob
        else:
            coords = [float_raise_nan(x.strip()) for x in ob.split(',')]

        wkid = 21781
        if len(coords) == 2:
            x, y = coords
            if x <= 180 and y <= 180:
                wkid = 4326
            elif x >= 485071.54 and x <= 828515.78 and y >= 75346.36 and y <= 299941.84:
                wkid = 21781
            elif x >= 2485071.58 and x <= 2828515.82 and y >= 1075346.31 and y <= 1299941.79:
                wkid = 2056

            crs = Named(properties=dict(name="urn:ogc:def:crs:EPSG:%d" % wkid))

            return geojson.geometry.Point(coords, crs=crs)

        if len(coords) == 4:
            crs = Named(properties=dict(name="urn:ogc:def:crs:EPSG:%d" % wkid))
            minx, miny, maxx, maxy = coords

            return geojson.geometry.Polygon(
                [[[minx, miny], [minx, maxy], [maxx, maxy], [maxx, miny], [minx, miny]]],
                crs=crs)

        else:
            raise ValueError("%r is not a simplified esri geometry", coords)


class EsriGeoJSON(dict):

    @classmethod
    def to_instance(cls, ob, default=None, strict=False):

        mapping = geojson.mapping.to_mapping(ob)

        d = dict((str(k), mapping[k]) for k in mapping)

        wkid = 21781
        if 'spatialReference' in d:
            ref = d['spatialReference']
            if 'wkid' in ref:
                wkid = ref['wkid']

        crs = Named(properties=dict(name="urn:ogc:def:crs:EPSG:%d" % wkid))

        if 'x' in d:
            coords = [d['x'], d['y']]

            return geojson.geometry.Point(coords, crs=crs)

        if 'xmin' in d:
            minx, miny, maxx, maxy = [d.get(k) for k in ['xmin', 'ymin', 'xmax', 'ymax']]
            coords = [[[minx, miny], [maxx, miny], [maxx, maxy], [minx, maxy], [minx, miny]]]

            return geojson.geometry.Polygon(coords, crs=crs)

        if 'paths' in d:
            coords = d['paths'][0]

            return geojson.geometry.LineString(coords, crs=crs)

        if 'rings' in d:
            coords = d['rings']

            return geojson.geometry.Polygon(coords, crs=crs)

        return d


def dumps(obj, sort_keys=False):
    encoder = EsriGeoJSONEncoder()
    obj = encoder.default(obj)
    return json.dumps(obj, sort_keys=sort_keys)


def loads(obj):

    try:
        return EsriSimple.to_instance(obj)

    except:
        return json.loads(obj,
                          object_hook=EsriGeoJSON.to_instance,
                          parse_constant=float_raise_nan
                          )
    else:
        raise ValueError("%r is not a recognized esri geometry type", obj)
