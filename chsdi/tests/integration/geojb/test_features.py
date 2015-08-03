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
            resp = self.testapp.get(self.features_url, params=self.params, status=200)
            self.failUnless(resp.content_type == 'application/json')

    def test_query_bbox(self):
        self.params['geometry'] = '588823.34,235243.77,589583.34,235733.77'
        self.params['geometryType'] = 'esriGeometryEnvelope'
        for layer_with_feature in registered_features['geojb']:
            self.params['layers'] = 'all:' + layer_with_feature
            resp = self.testapp.get(self.features_url, params=self.params, status=200)
            self.failUnless(resp.content_type == 'application/json')

    def test_query_no_geometry(self):
        self.params['layers'] = 'all:' + self.test_config['layer_id']
        self.params['returnGeometry'] = 'false'
        resp = self.testapp.get(self.features_url, params=self.params, status=200)
        self.failUnless(resp.content_type == 'application/json')
        self.failUnless('geometry' not in resp.json['results'][0])

    def test_properties_names(self):
        for layer_with_feature in registered_features['geojb']:
            self.params['layers'] = 'all:' + layer_with_feature
            resp = self.testapp.get(self.features_url, params=self.params, status=200)
            self.failUnless(resp.content_type == 'application/json')
            self.failUnless(len(resp.json['propertiesNames']) > 0)
            for layer_id in resp.json['propertiesNames']:
                self.failUnless(len(resp.json['propertiesNames'][layer_id]) > 0)

    def test_query_geometry(self):
        self.params['layers'] = 'all:' + self.test_config['layer_id']
        self.params['returnGeometry'] = 'true'
        resp = self.testapp.get(self.features_url, params=self.params, status=200)
        self.failUnless(resp.content_type == 'application/json')
        self.failUnless('geometry' in resp.json['results'][0])

        del self.params['returnGeometry']
        resp = self.testapp.get(self.features_url, params=self.params, status=200)
        self.failUnless(resp.content_type == 'application/json')
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
        self.failUnless(resp.content_type == 'application/json')
        self.failUnless(len(resp.json) == 1)
        self.failUnless(resp.json['feature']['id'] == self.feature_id)

    def test_identify_feature_inexistant_layer(self):
        self.features_url = '/'.join(self.features_url.split('/')[:-2])
        self.features_url += '/dummy/1'
        self.testapp.get(self.features_url, status=400)

    def test_identify_inexistant_feature(self):
        self.features_url = '/'.join(self.features_url.split('/')[:-1])
        self.features_url += '/1'
        self.testapp.get(self.features_url, status=404)

    def test_identify_mutliple_features(self):
        url = '{},{}'.format(self.features_url, self.complementary_feature_id)
        resp = self.testapp.get(url, status=200)
        self.failUnless(resp.content_type == 'application/json')
        self.failUnless(len(resp.json['features']) == 2)
        self.failUnless(resp.json['features'][0]['feature']['id'] == self.feature_id)
        self.failUnless(resp.json['features'][1]['feature']['id'] == self.complementary_feature_id)


class TestFeatureFind(TestsBase):
    def setUp(self):
        super().setUp()
        self.feature_find_url = '/rest/services/geojb/MapServer/find'
        self.params = {
            'layer': self.test_config['layer_id'],
            'searchText': 'jardin',
            'searchField': 'genre_fr',
        }

    def test_find_wrong_parameters(self):
        self.testapp.get(self.feature_find_url, status=400)
        params = {'layers': self.test_config['layer_id']}
        self.testapp.get(self.feature_find_url, params=params, status=400)
        params['searchText'] = 'jardin'
        self.testapp.get(self.feature_find_url, params=params, status=400)
        del params['searchText']
        params['searchField'] = 'genre_fr'
        self.testapp.get(self.feature_find_url, params=params, status=400)

    def test_find_wrong_field(self):
        self.params['searchField'] = 'dummy'
        self.testapp.get(self.feature_find_url, params=self.params, status=400)

    def test_find_wrong_layer(self):
        self.params['layer'] = 'dummy'
        self.testapp.get(self.feature_find_url, params=self.params, status=400)

    def test_find(self):
        resp = self.testapp.get(self.feature_find_url, params=self.params, status=200)
        self.failUnless(resp.content_type == 'application/json')
        self.failUnless(len(resp.json['results']) > 0)
        self.failUnless('geometry' in resp.json['results'][0])

    def test_find_no_geometry(self):
        self.params['returnGeometry'] = 'false'
        resp = self.testapp.get(self.feature_find_url, params=self.params, status=200)
        self.failUnless(resp.content_type == 'application/json')
        self.failUnless(len(resp.json['results']) > 0)
        self.failUnless('geometry' not in resp.json['results'][0])

    def test_find_geometry(self):
        self.params['returnGeometry'] = 'true'
        resp = self.testapp.get(self.feature_find_url, params=self.params, status=200)
        self.failUnless(resp.content_type == 'application/json')
        self.failUnless(len(resp.json['results']) > 0)
        self.failUnless('geometry' in resp.json['results'][0])

    def test_find_no_match(self):
        self.params['searchText'] = 'not_a_genre'
        resp = self.testapp.get(self.feature_find_url, params=self.params, status=200)
        self.failUnless(resp.content_type == 'application/json')
        self.failUnless(len(resp.json['results']) == 0)

    def test_find_contains(self):
        self.params['contains'] = 'true'
        resp = self.testapp.get(self.feature_find_url, params=self.params, status=200)
        self.failUnless(resp.content_type == 'application/json')
        self.failUnless(len(resp.json['results']) > 0)

        self.setUp()
        self.params['searchText'] = 'jardi'
        resp = self.testapp.get(self.feature_find_url, params=self.params, status=200)
        self.failUnless(resp.content_type == 'application/json')
        self.failUnless(len(resp.json['results']) > 0)

        self.setUp()
        self.params['contains'] = 'false'
        self.params['searchText'] = 'jardi'
        resp = self.testapp.get(self.feature_find_url, params=self.params, status=200)
        self.failUnless(resp.content_type == 'application/json')
        self.failUnless(len(resp.json['results']) == 0)

        self.setUp()
        self.params['searchText'] = 'jardin'
        resp = self.testapp.get(self.feature_find_url, params=self.params, status=200)
        self.failUnless(resp.content_type == 'application/json')
        self.failUnless(len(resp.json['results']) > 0)
