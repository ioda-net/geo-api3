from chsdi.tests.integration import TestsBase
from chsdi.models import registered_features


class TestFeatures(TestsBase):
    def setUp(self):
        super().setUp()
        self.features_url = '/rest/services/geojb/MapServer/identify'
        self.params = {
            'geometryFormat': 'geojson',
            'geometry': '589635.84,235603.77',
            'geometryType': 'esriGeometryPoint',
            'imageDisplay': '1920,778,96',
            'mapExtent': '586810.84,234543.77,591610.84,236488.77',
            'tolerance': 5,
        }

    def test_no_params(self):
        self.testapp.get(self.features_url, status=404)
        params = {'geometryFormat': 'geojson'}
        self.testapp.get(self.features_url, params=params, status=400)
        params['geometry'] = '589635.84,235603.77'
        self.testapp.get(self.features_url, params=params, status=400)
        params['geometryType'] = 'esriGeometryPoint'
        self.testapp.get(self.features_url, params=params, status=400)
        params['imageDisplay'] = '1920,778,96'
        self.testapp.get(self.features_url, params=params, status=400)
        params['mapExtent'] = '586810.84,234543.77,591610.84,236488.77'
        self.testapp.get(self.features_url, params=params, status=400)
        params['tolerance'] = 5
        self.testapp.get(self.features_url, params=params, status=400)

    def test_no_layers(self):
        self.testapp.get(self.features_url, params=self.params, status=400)

    def test_query(self):
        for layer_with_feature in registered_features['geojb']:
            self.params['layers'] = 'all:' + layer_with_feature
            self.testapp.get(self.features_url, params=self.params, status=200)

    def test_query_bbox(self):
        self.params['geometry'] = '588823.34,235243.77,589583.34,235733.77'
        self.params['geometryType'] = 'esriGeometryEnvelope'
        for layer_with_feature in registered_features['geojb']:
            self.params['layers'] = 'all:' + layer_with_feature
            self.testapp.get(self.features_url, params=self.params, status=200)
