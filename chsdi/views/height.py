from chsdi.lib.validation.height import HeightValidation
from chsdi.lib.raster.georaster import get_raster

from pyramid.view import view_config


class Height(HeightValidation):

    def __init__(self, request):
        super().__init__()
        self.elevation_models = request.params.get('elevationModel')
        if 'easting' in request.params:
            self.lon = request.params.get('easting')
        else:
            self.lon = request.params.get('lon')
        if 'northing' in request.params:
            self.lat = request.params.get('northing')
        else:
            self.lat = request.params.get('lat')
        self.request = request

    @view_config(route_name='height', renderer='jsonp', http_cache=0)
    def height(self):
        rasters = [get_raster(layer) for layer in self.elevation_models]
        alt = self._filter_alt(rasters[0].getVal(self.lon, self.lat))
        alt = alt if alt is not None else ''

        return {'height': str(alt)}

    def _filter_alt(self, alt):
        if alt is not None and alt > 0.0:
            # 10cm accuracy is enough for altitudes
            return round(alt * 10.0) / 10.0
        else:
            return None
