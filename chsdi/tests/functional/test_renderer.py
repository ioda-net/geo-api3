import unittest
import json

from pyramid import testing


class TestEsriGeoJSON(unittest.TestCase):

    def _call_fut(self, **kwargs):
        from chsdi.renderers import EsriJSON
        fake_info = {}
        return EsriJSON(**kwargs)(fake_info)

    def test_json(self):
        renderer = self._call_fut()
        result = renderer({'a': 1}, {})
        self.assertEqual(result, '{"a": 1}')

    def test_geojson(self):
        from geojson import Point
        f = Point([600000, 200000], properties={'name': 'toto'})
        renderer = self._call_fut()
        request = testing.DummyRequest()
        result = renderer(f, {'request': request})
        expected_result = {
            "spatialReference": {"wkid": 21781},
            "attributes": {"name": "toto"},
            "y": 200000,
            "x": 600000
        }
        self.assertEqual(json.loads(result), expected_result)

        self.assertEqual(request.response.content_type, 'application/json')

    def test_jsonp(self):
        renderer = self._call_fut(jsonp_param_name="cb")
        from geojson import Point
        f = Point([600000, 200000], properties={'name': 'toto'})
        request = testing.DummyRequest()
        request.params['cb'] = 'jsonp_cb'
        result = renderer(f, {'request': request})
        expected_result = {
            "x": 600000,
            "attributes": {"name": "toto"},
            "y": 200000, "spatialReference":
            {"wkid": 21781}
        }
        self.assertEqual(json.loads(result[9:-2]), expected_result)
        self.assertEqual(request.response.content_type, 'text/javascript')
