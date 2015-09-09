from pyramid.httpexceptions import HTTPBadRequest
from shapely.geometry import asShape

from chsdi.lib.helpers import get_from_configuration


class ProfileValidation:
    def __init__(self):
        self._linestring = None
        self._elevation_models = None
        self._nb_points = None
        self._ma_offset = None

    @property
    def linestring(self):
        return self._linestring

    @property
    def elevation_models(self):
        return self._elevation_models

    @property
    def nb_points(self):
        return self._nb_points

    @property
    def ma_offset(self):
        return self._ma_offset

    @linestring.setter
    def linestring(self, value):
        import geojson
        if value is None:
            raise HTTPBadRequest("Missing parameter geom")
        try:
            geom = geojson.loads(value, object_hook=geojson.GeoJSON.to_instance)
        except:
            raise HTTPBadRequest("Error loading geometry in JSON string")
        try:
            shape = asShape(geom)
        except:  # pragma: no cover
            raise HTTPBadRequest("Error converting JSON to Shape")
        try:
            shape.is_valid
        except:
            raise HTTPBadRequest("Invalid Linestring syntax")

        self._linestring = shape

    @elevation_models.setter
    def elevation_models(self, value):
        if value is None:
            available_rasters = get_from_configuration('raster.available').split(',')
            self._elevation_models = [model.strip() for model in available_rasters]
        else:
            value = value.split(',')
            for i in value:
                if i not in get_from_configuration('raster.available'):
                    raise HTTPBadRequest(
                        "Please provide a valid name for the elevation model DTM25, DTM2 or COMB")
            value.sort()
            self._elevation_models = value

    @nb_points.setter
    def nb_points(self, value):
        if value is None:
            self._nb_points = 200
        else:
            if value.isdigit():
                self._nb_points = int(value)
            else:
                raise HTTPBadRequest(
                    "Please provide a numerical value for the parameter 'NbPoints'")

    @ma_offset.setter
    def ma_offset(self, value):
        if value is None:
            self._ma_offset = 3
        else:
            if value.isdigit():
                self._ma_offset = int(value)
            else:
                raise HTTPBadRequest("Please provide a numerical value for the parameter 'offset'")
