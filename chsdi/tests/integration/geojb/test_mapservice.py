import json

from chsdi.tests.integration import TestsBase


def getLayers(query):
    for q in query:
        yield q[0]


class TestMapServiceView(TestsBase):
    def test_identify_nan_error(self):
        geom = {
            "rings": [
                [
                    [675000, 245000],
                    [670000, 255000],
                    [680000, 260000],
                    [690000, 255000],
                    [685000, 240000],
                    [675000, 245000]
                ]
            ]
        }
        params = {
            'geometry': json.dumps(geom),
            'geometryType': 'esriGeometryPolygon', 'imageDisplay': '500,600,96',
            'mapExtent': 'NaN,147956,549402,148103.5',
            'tolerance': '0',
            'layers': 'all:' + self.test_config['layer_id']
        }
        resp = self.testapp.get(
            '/rest/services/geojb/MapServer/identify',
            params=params,
            status=400)
        resp.mustcontain('Please provide numerical values for the parameter mapExtent')
        params = {
            'geometryType': 'esriGeometryPoint',
            'geometry': '600000,NaN,549402,148103.5',
            'imageDisplay': '500,600,96',
            'mapExtent': '548945.5,147956,549402,148103.5',
            'tolerance': '1',
            'layers': 'all'
        }
        resp = self.testapp.get('/rest/services/ech/MapServer/identify', params=params, status=400)
        resp.mustcontain('Please provide a valid geometry')
        wrong_geom = {
            "rings": '[[[NaN,NaN],[NaN,NaN]' +
            ',[680000,260000],[690000,255000],[685000,240000],[675000,245000]]]'
        }
        params = {
            'geometry': json.dumps(wrong_geom),
            'geometryType': 'esriGeometryPolygon',
            'imageDisplay': '500,600,96',
            'mapExtent': '600000,147956,549402,148103.5',
            'tolerance': '0',
            'layers': 'all:' + self.test_config['layer_id']
        }
        resp = self.testapp.get('/rest/services/all/MapServer/identify', params=params, status=400)
        resp.mustcontain('Please provide a valid geometry')
        params = {
            'geometry': json.dumps(geom),
            'geometryType': 'esriGeometryPolygon',
            'imageDisplay': '500,NaN,96',
            'mapExtent': '548945.5,147956,549402,148103.5',
            'tolerance': '0',
            'layers': 'all:' + self.test_config['layer_id']
        }
        resp = self.testapp.get('/rest/services/all/MapServer/identify', params=params, status=400)
        resp.mustcontain('Please provide numerical values for the parameter imageDisplay')
        params = {
            'geometry': json.dumps(geom),
            'geometryType': 'esriGeometryPolyline',
            'imageDisplay': '500,600,96',
            'mapExtent': '548945.5,147956,549402,148103.5',
            'tolerance': 'NaN',
            'layers': 'all:' + self.test_config['layer_id']
        }
        resp = self.testapp.get('/rest/services/all/MapServer/identify', params=params, status=400)
        resp.mustcontain('Please provide a float value for the pixel tolerance')
