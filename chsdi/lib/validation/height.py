from pyramid.httpexceptions import HTTPBadRequest

from chsdi.lib.helpers import get_from_configuration


class HeightValidation:

    def __init__(self):
        self._lon = None
        self._lat = None
        self._elevation_models = None

    @property
    def lon(self):
        return self._lon

    @property
    def lat(self):
        return self._lat

    @property
    def elevation_models(self):
        return self._elevation_models

    @lon.setter
    def lon(self, value):
        if value is None:
            raise HTTPBadRequest("Missing parameter 'easting'/'lon'")
        try:
            self._lon = float(value)
        except ValueError:
            raise HTTPBadRequest("Please provide numerical values for the parameter 'easting'/'lon'")

    @lat.setter
    def lat(self, value):
        if value is None:
            raise HTTPBadRequest("Missing parameter 'norhting'/'lat'")
        try:
            self._lat = float(value)
        except ValueError:
            raise HTTPBadRequest("Please provide numerical values for the parameter 'northing'/'lat'")

    @elevation_models.setter
    def elevation_models(self, value):
        if value is None:
            value = get_from_configuration('raster.available')

        if not isinstance(value, list):
            value = [model.strip() for model in value.split(',')]
            for i in value:
                if i not in get_from_configuration('raster.available'):
                    raise HTTPBadRequest("Please provide a valid name for the elevation model DTM25, DTM2 or COMB")
        self._elevation_models = value
