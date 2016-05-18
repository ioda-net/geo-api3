from chsdi.tests.integration import TestsBase


class TestSearchServiceView(TestsBase):
    def setUp(self):
        super().setUp()
        self.portal_name = 'geojb'
        self.search_uri = '/rest/services/{}/SearchServer'.format(self.portal_name)

    def test_no_type(self):
        self.testapp.get(self.search_uri, params={'searchText': 'ga'}, status=400)

    def test_inexistant_type(self):
        self.testapp.get(
            self.search_uri,
            params={'searchText': 'ga', 'type': 'gnu_linux'},
            status=400)

    def test_no_search_text(self):
        self.testapp.get(self.search_uri, params={'type': 'layers'}, status=400)

    def test_wrong_bbox(self):
        # Wrong number
        params = {'searchText': 'couverture', 'type': 'layers', 'bbox': '789.52,456.54'}
        self.testapp.get(self.search_uri, params=params, status=400)
        # Wrong separator
        params = {'searchText': 'couverture', 'type': 'layers', 'bbox': '789.52|456.54'}
        self.testapp.get(self.search_uri, params=params, status=400)
        # Not numeric
        params = {'searchText': 'couverture', 'type': 'layers', 'bbox': '2,aaa,bbbb,2'}
        self.testapp.get(self.search_uri, params=params, status=400)
        # Invalid coords for Swiss
        params = {'searchText': 'couverture', 'type': 'layers', 'bbox': '420000,420001,0,2'}
        self.testapp.get(self.search_uri, params=params, status=400)
        params = {'searchText': 'couverture', 'type': 'layers', 'bbox': '2,0,420000,420001'}
        self.testapp.get(self.search_uri, params=params, status=400)


class TestSearchLayers(TestSearchServiceView):
    def test_search_layers(self):
        params = {'searchText': self.layer_id, 'type': 'layers'}
        resp = self.testapp.get(self.search_uri, params=params, status=200)
        self.assertTrue(resp.content_type == 'application/json')

    def test_search_layers_with_cb(self):
        params = {'searchText': self.layer_id, 'type': 'layers', 'callback': 'callback'}
        resp = self.testapp.get(self.search_uri, params=params, status=200)
        self.assertTrue(resp.content_type == 'application/javascript')

    def test_search_layers_for_one_layer(self):
        params = {'searchText': self.layer_id, 'type': 'layers', 'limit': 1, 'lang': 'fr'}
        resp = self.testapp.get(self.search_uri, params=params, status=200)
        self.assertTrue(resp.content_type == 'application/json')
        self.assertTrue(len(resp.json['results']) == 1)

        params = {'searchText': self.layer_id, 'type': 'layers', 'limit': 2, 'lang': 'fr'}
        resp = self.testapp.get(self.search_uri, params=params, status=200)
        self.assertTrue(resp.content_type == 'application/json')
        self.assertTrue(len(resp.json['results']) == 2)

    def test_search_layers_accents(self):
        params = {'searchText': '*%+&/()=?!üäöéà$@i£$', 'type': 'layers'}
        resp = self.testapp.get(self.search_uri, params=params, status=200)
        self.assertTrue(resp.content_type == 'application/json')
        self.assertTrue(len(resp.json['results']) == 0)


class TestSearchLocations(TestSearchServiceView):
    def test_search_locations_no_text(self):
        params = {
            'searchText': '',
            'type': 'locations',
            'bbox': '551306.5625,167918.328125,551754.125,168514.625'
        }
        resp = self.testapp.get(self.search_uri, params=params, status=200)
        self.assertTrue(resp.content_type == 'application/json')
        params = {'type': 'locations', 'bbox': '551306.5625,167918.328125,551754.125,168514.625'}
        resp = self.testapp.get(self.search_uri, params=params, status=200)
        self.assertTrue(resp.content_type == 'application/json')

    def test_search_locations(self):
        params = {
            'searchText': 'rue des oeuches',
            'type': 'locations',
            'bbox': '551306.5625,167918.328125,551754.125,168514.625'
        }
        resp = self.testapp.get(self.search_uri, params=params, status=200)
        self.assertTrue(resp.content_type == 'application/json')

    def test_search_loactions_with_cb(self):
        params = {
            'searchText': 'rue des oeuches',
            'type': 'locations',
            'bbox': '551306.5625,167918.328125,551754.125,168514.625',
            'callback': 'callback'
        }
        resp = self.testapp.get(self.search_uri, params=params, status=200)
        self.assertTrue(resp.content_type == 'application/javascript')

    def test_search_locations_point(self):
        params = {
            'searchText': 'rue des oeuches',
            'type': 'locations',
            'bbox': '594870.8,236234.7,594870.8,236234.7'
        }
        resp = self.testapp.get(self.search_uri, params=params, status=200)
        self.assertTrue(resp.content_type == 'application/json')

    def test_search_locations_prefix_sentence_match(self):
        params = {
            'searchText': 'Péry-La',
            'type': 'locations'
        }
        resp = self.testapp.get(self.search_uri, params=params, status=200)
        self.assertTrue(resp.content_type == 'application/json')
        self.assertTrue(resp.json['results'][0]['attrs']['search_string'] == 'pery-la heutte')
        self.assertTrue(resp.json['results'][0]['attrs']['origin'] == 'communes')

    def test_search_locations_grandval(self):
        params = {'searchText': 'Grandval', 'type': 'locations'}
        resp = self.testapp.get(self.search_uri, params=params, status=200)
        self.assertTrue(resp.content_type == 'application/json')
        self.assertTrue(resp.json['results'][0]['attrs']['search_string'] == 'grandval')

    def test_search_locations_mou(self):
        params = {'searchText': 'mou', 'type': 'locations'}
        resp = self.testapp.get(self.search_uri, params=params, status=200)
        self.assertTrue(resp.content_type == 'application/json')
        self.assertTrue(resp.json['results'][0]['attrs']['search_string'][:3] == 'mou')

    def test_search_locations_accent(self):
        params = {'searchText': 'Corgémont, Rue de l\'Envers, 19', 'type': 'locations'}
        resp = self.testapp.get(self.search_uri, params=params, status=200)
        self.assertTrue(resp.content_type == 'application/json')
        expected_detail = resp.json['results'][0]['attrs']['search_string']
        self.assertTrue(expected_detail == 'corgemont, rue de l\'envers, 19')

    def test_search_locations_moutier_oeuches(self):
        params = {'searchText': 'moutier oeuches', 'type': 'locations'}
        resp = self.testapp.get(self.search_uri, params=params, status=200)
        self.assertTrue(resp.content_type == 'application/json')
        self.assertTrue('moutier' in resp.json['results'][0]['attrs']['search_string'])
        self.assertTrue('oeuches' in resp.json['results'][0]['attrs']['search_string'])

    def test_search_location_max_address(self):
        params = {'searchText': 'moutier', 'type': 'locations'}
        resp = self.testapp.get(self.search_uri, params=params, status=200)
        self.assertTrue(resp.content_type == 'application/json')
        results_addresses = [result for result in resp.json['results']]
        self.assertTrue(len(results_addresses) <= 50)

    def test_search_locations_no_geometry(self):
        params = {'searchText': 'moutier', 'type': 'locations', 'returnGeometry': 'false'}
        resp = self.testapp.get(self.search_uri, params=params, status=200)
        self.assertTrue(resp.content_type == 'application/json')
        self.assertTrue('geom_st_box2d' not in resp.json['results'][0]['attrs'].keys())

    def test_locations_searchtext_apostrophe(self):
        params = {'searchText': 'corgemont, Rue de l\'Envers', 'type': 'locations'}
        resp = self.testapp.get(self.search_uri, params=params, status=200)
        self.assertTrue(resp.content_type == 'application/json')
        expected_detail = resp.json['results'][0]['attrs']['search_string']
        self.assertTrue(expected_detail.startswith('corgemont, rue de l\'envers'))

    def test_order_addresses(self):
        params = {'searchText': 'moutier, chemin de graitery', 'type': 'locations'}
        resp = self.testapp.get(self.search_uri, params=params, status=200)
        self.assertTrue(resp.content_type == 'application/json')
        self.assertTrue(
            resp.json['results'][0]['attrs']['search_string'] == 'moutier, chemin de graitery, 1')
        self.assertTrue(
            resp.json['results'][1]['attrs']['search_string'] == 'moutier, chemin de graitery, 1a')
        self.assertTrue(
            resp.json['results'][7]['attrs']['search_string'] == 'moutier, chemin de graitery, 10')
        self.assertTrue(
            resp.json['results'][8]['attrs']['search_string'] == 'moutier, chemin de graitery, 12')
        resp_attr = resp.json['results'][9]['attrs']['search_string']
        expected_resp = 'moutier, chemin de graitery, 12a'
        self.assertTrue(resp_attr == expected_resp)

    def test_order_communes_addresses(self):
        params = {'searchText': 'cor', 'type': 'locations'}
        resp = self.testapp.get(self.search_uri, params=params, status=200)
        self.assertTrue(resp.content_type == 'application/json')
        self.assertTrue(resp.json['results'][0]['attrs']['search_string'] == 'corcelles _be_')
        self.assertTrue(resp.json['results'][1]['attrs']['search_string'] == 'corgemont')
        self.assertTrue(resp.json['results'][2]['attrs']['search_string'] == 'cormoret')
        self.assertTrue(resp.json['results'][3]['attrs']['search_string'] == 'cortebert')
        self.assertTrue(len(resp.json['results']) == 50)

    def test_search_address_with_letters(self):
        params = {'searchText': 'Rue des Oeuches, 86', 'type': 'locations'}
        resp = self.testapp.get(self.search_uri, params=params, status=200)
        self.assertTrue(resp.content_type == 'application/json')

    def test_search_locations_escape_charachters(self):
        params = {'searchText': 'la fe', 'type': 'locations'}
        resp = self.testapp.get(self.search_uri, params=params, status=200)
        self.assertTrue(len(resp.json['results']) > 0)

    def test_search_locations_authorized(self):
        params = {'searchText': 'moutier', 'type': 'locations'}
        resp = self.testapp.get(self.search_uri, params=params, status=200)
        self.assertTrue(resp.content_type == 'application/json')
        self.assertTrue('geom_st_box2d' in resp.json['results'][0]['attrs'].keys())

    def test_search_locations_authorized_no_geometry(self):
        params = {'searchText': 'moutier', 'type': 'locations', 'returnGeometry': 'false'}
        resp = self.testapp.get(self.search_uri, params=params,
                                headers=dict(HTTP_X_SEARCHSERVER_AUTHORIZED='true'), status=200)
        self.assertTrue(resp.content_type == 'application/json')
        self.assertTrue('geom_st_box2d' not in resp.json['results'][0]['attrs'].keys())

    def test_search_locations_one_origin(self):
        params = {'searchText': 'moutier', 'type': 'locations', 'origins': 'communes'}
        resp = self.testapp.get(self.search_uri, params=params, status=200)
        self.assertTrue(len(resp.json['results']) == 1)

    def test_search_locations_several_origins(self):
        params = {
            'searchText': 'moutier',
            'type': 'locations',
            'origins': 'communes,sorted_buildings'
        }
        resp = self.testapp.get(self.search_uri, params=params, status=200)
        self.assertTrue(len(resp.json['results']) > 1)

    def test_search_locations_bad_origin(self):
        params = {'searchText': 'moutier', 'type': 'locations', 'origins': 'dummy'}
        self.testapp.get(self.search_uri, params=params, status=400)

    def test_search_locations_with_bbox(self):
        params = {
            'type': 'locations',
            'searchText': 'moutier, rue des oeuches, 45a',
            'bbox': '550000,210000,620000,245000'
        }
        resp = self.testapp.get(self.search_uri, params=params, status=200)
        self.assertTrue(
            resp.json['results'][0]['attrs']['search_string'] == 'moutier, rue des oeuches, 45a')
        self.assertTrue(len(resp.json['results']) == 1)

    def test_search_locations_bbox_only(self):
        params = {'type': 'locations', 'bbox': '550000,210000,620000,245000'}
        resp = self.testapp.get(self.search_uri, params=params, status=200)
        self.assertTrue(resp.content_type == 'application/json')
        self.assertTrue(len(resp.json['results']) > 1)

    def test_search_locations_noparams(self):
        params = {'type': 'locations'}
        self.testapp.get(self.search_uri, params=params, status=400)

    def test_location_ofs(self):
        params = {'searchText': '449', 'type': 'locations'}
        resp = self.testapp.get(self.search_uri, params=params, status=200)
        self.assertTrue(len(resp.json['results']) > 0)

    def test_location_ofs_arr(self):
        params = {'searchText': '1449', 'type': 'locations'}
        resp = self.testapp.get(self.search_uri, params=params, status=200)
        self.assertTrue(len(resp.json['results']) > 0)

    def test_location_wrong_ofs(self):
        params = {'searchText': '10000000000', 'type': 'locations'}
        resp = self.testapp.get(self.search_uri, params=params, status=200)
        self.assertTrue(len(resp.json['results']) == 0)

    def test_locations_search_limit(self):
        params = {'searchText': 'moutier', 'type': 'locations', 'limit': '1'}
        resp = self.testapp.get(self.search_uri, params=params, status=200)
        self.assertTrue(len(resp.json['results']) == 1)
        self.assertTrue(resp.json['results'][0]['attrs']['search_string'] == 'moutier')

    def test_locations_search_wrong_limit(self):
        params = {'searchText': 'moutier', 'type': 'locations', 'limit': '5.5'}
        self.testapp.get(self.search_uri, params=params, status=400)

    def test_search_max_words(self):
        params = {
            'searchText': 'this is a text with exactly 10 words, should work',
            'type': 'locations',
            'bbox': '551306.5625,167918.328125,551754.125,168514.625'
        }
        self.testapp.get('/rest/services/all/SearchServer', params=params, status=200)
        params = {
            'searchText': 'this is a text with exactly 10 words, should work',
            'type': 'layers',
            'bbox': '551306.5625,167918.328125,551754.125,168514.625'
        }
        self.testapp.get('/rest/services/all/SearchServer', params=params, status=200)
        params = {
            'searchText': 'this is a text with exactly 11 words, should NOT work',
            'type': 'locations',
            'bbox': '551306.5625,167918.328125,551754.125,168514.625'
        }
        self.testapp.get('/rest/services/all/SearchServer', params=params, status=400)
        params = {
            'searchText': 'this is a text with exactly 11 words, should NOT work',
            'type': 'layers',
            'bbox': '551306.5625,167918.328125,551754.125,168514.625'
        }
        self.testapp.get('/rest/services/all/SearchServer', params=params, status=400)

    def test_search_with_keyword(self):
        params = {'searchText': 'address moutier', 'type': 'locations', 'limit': '1'}
        resp = self.testapp.get(self.search_uri, params=params, status=200)
        self.assertTrue(resp.json['results'][0]['attrs']['search_string'] == 'moutier')

        params = {'searchText': 'parcel 123', 'type': 'locations', 'limit': '1'}
        resp = self.testapp.get(self.search_uri, params=params, status=200)
        self.assertTrue(
            resp.json['results'][0]['attrs']['search_string'] == 'corgemont, 123 ch887046354323')
