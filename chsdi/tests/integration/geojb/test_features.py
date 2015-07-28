from chsdi.tests.integration import TestsBase
from chsdi.models import registered_features


class TestFeaturesIdentify(TestsBase):
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

    def test_query_no_geometry(self):
        self.params['layers'] = 'all:' + self.test_config['layer_id']
        self.params['returnGeometry'] = 'false'
        resp = self.testapp.get(self.features_url, params=self.params, status=200)
        self.failUnless('geometry' not in resp.json['results'][0])

    def test_query_geometry(self):
        self.params['layers'] = 'all:' + self.test_config['layer_id']
        self.params['returnGeometry'] = 'true'
        resp = self.testapp.get(self.features_url, params=self.params, status=200)
        self.failUnless('geometry' in resp.json['results'][0])
        del self.params['returnGeometry']
        resp = self.testapp.get(self.features_url, params=self.params, status=200)
        self.failUnless('geometry' in resp.json['results'][0])


class TestFeature(TestsBase):
    def setUp(self):
        super().setUp()
        self.feature_id = 1109266
        self.complementary_feature_id = 1109267
        self.features_url = \
            '/rest/services/geojb/MapServer/{layer_id}/{feature_id}'\
            .format(
                layer_id=self.test_config['layer_id'],
                feature_id=self.feature_id)

    def test_identify_feature(self):
        resp = self.testapp.get(self.features_url, status=200)
        self.failUnless(len(resp.json) == 1)
        self.failUnless(resp.json['feature']['id'] == self.feature_id)

    def test_identify_mutliple_features(self):
        url = '{},{}'.format(self.features_url, self.complementary_feature_id)
        resp = self.testapp.get(url, status=200)
        self.failUnless(len(resp.json['features']) == 2)
        self.failUnless(resp.json['features'][0]['feature']['id'] == self.feature_id)
        self.failUnless(resp.json['features'][1]['feature']['id'] == self.complementary_feature_id)
