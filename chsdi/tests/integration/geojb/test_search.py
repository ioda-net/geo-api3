import unittest
from chsdi.tests.integration import TestsBase


class TestSearchServiceView(TestsBase):
    def setUp(self):
        super().setUp()
        self.portal_name = 'geojb'
        self.search_uri = '/rest/services/{}/SearchServer'.format(self.portal_name)
        self.address_origins = self.config['template']['search']['address_origins']

    def test_no_type(self):
        self.testapp.get(self.search_uri, params={'searchText': 'ga'}, status=400)


class TestSearchLayers(TestSearchServiceView):
    def test_search_layers(self):
        resp = self.testapp.get(self.search_uri, params={'searchText': self.layer_id, 'type': 'layers'}, status=200)
        self.failUnless(resp.content_type == 'application/json')

    def test_search_layers_with_cb(self):
        resp = self.testapp.get(self.search_uri, params={'searchText': self.layer_id, 'type': 'layers', 'callback': 'callback'}, status=200)
        self.failUnless(resp.content_type == 'application/javascript')

    def test_search_layers_for_one_layer(self):
        resp = self.testapp.get(self.search_uri, params={'searchText': self.layer_id, 'type': 'layers', 'limit': 1}, status=200)
        self.failUnless(resp.content_type == 'application/json')
        self.failUnless(len(resp.json['results']) == 1)

    def test_search_layers_accents(self):
        resp = self.testapp.get(self.search_uri, params={'searchText': '*%+&/()=?!üäöéà$@i£$', 'type': 'layers'}, status=200)
        self.failUnless(resp.content_type == 'application/json')
        self.failUnless(len(resp.json['results']) == 0)


class TestSearchLocations(TestSearchServiceView):
    def test_search_locations(self):
        resp = self.testapp.get(self.search_uri, params={'searchText': 'rue des oeuches', 'type': 'locations', 'bbox': '551306.5625,167918.328125,551754.125,168514.625'}, status=200)
        self.failUnless(resp.content_type == 'application/json')

    def test_search_loactions_with_cb(self):
        resp = self.testapp.get(self.search_uri, params={'searchText': 'rue des oeuches', 'type': 'locations', 'bbox': '551306.5625,167918.328125,551754.125,168514.625', 'callback': 'callback'}, status=200)
        self.failUnless(resp.content_type == 'application/javascript')

    def test_search_locations_all_langs(self):
        # even if not lang dependent
        for lang in self.langs:
            resp = self.testapp.get(self.search_uri, params={'searchText': 'mont d\'or', 'type': 'locations', 'bbox': '551306.5625,167918.328125,551754.125,168514.625', 'lang': lang}, status=200)
            self.failUnless(resp.content_type == 'application/json')

    def test_search_locations_prefix_sentence_match(self):
        resp = self.testapp.get(self.search_uri, params={'searchText': 'Péry-La', 'type': 'locations'}, status=200)
        self.failUnless(resp.content_type == 'application/json')
        self.failUnless(resp.json['results'][0]['attrs']['detail'] == 'pery-la heutte')
        self.failUnless(resp.json['results'][0]['attrs']['origin'] == 'communes')

    def test_search_locations_grandval(self):
        resp = self.testapp.get(self.search_uri, params={'searchText': 'Grandval', 'type': 'locations'}, status=200)
        self.failUnless(resp.content_type == 'application/json')
        self.failUnless(resp.json['results'][0]['attrs']['detail'] == 'grandval')

    def test_search_locations_mou(self):
        resp = self.testapp.get(self.search_uri, params={'searchText': 'mou', 'type': 'locations'}, status=200)
        self.failUnless(resp.content_type == 'application/json')
        self.failUnless(resp.json['results'][0]['attrs']['detail'][:3] == 'mou')

    def test_search_locations_accent(self):
        resp = self.testapp.get(self.search_uri, params={'searchText': 'Corgémont, Rue de l\'Envers, 19', 'type': 'locations'}, status=200)
        self.failUnless(resp.content_type == 'application/json')
        self.failUnless(resp.json['results'][0]['attrs']['detail'] == 'corgemont, rue de l\'envers, 19')

    def test_search_locations_moutier_oeuches(self):
        resp = self.testapp.get(self.search_uri, params={'searchText': 'moutier oeuches', 'type': 'locations'}, status=200)
        self.failUnless(resp.content_type == 'application/json')
        self.failUnless('moutier' in resp.json['results'][0]['attrs']['detail'])
        self.failUnless('oeuches' in resp.json['results'][0]['attrs']['detail'])

    def test_search_location_max_address(self):
        resp = self.testapp.get(self.search_uri, params={'searchText': 'moutier', 'type': 'locations'}, status=200)
        self.failUnless(resp.content_type == 'application/json')
        results_addresses = [result for result in resp.json['results'] if result['attrs']['origin'] in self.address_origins]
        self.failUnless(len(results_addresses) <= 50)

    def test_search_locations_no_geometry(self):
        resp = self.testapp.get(self.search_uri, params={'searchText': 'moutier', 'type': 'locations', 'returnGeometry': 'false'}, status=200)
        self.failUnless(resp.content_type == 'application/json')
        self.failUnless('geom_st_box2d' not in resp.json['results'][0]['attrs'].keys())

    def test_locations_searchtext_apostrophe(self):
        resp = self.testapp.get(self.search_uri, params={'searchText': 'corgemont, Rue de l\'Envers', 'type': 'locations'}, status=200)
        self.failUnless(resp.content_type == 'application/json')
        self.failUnless(resp.json['results'][0]['attrs']['detail'].startswith('corgemont, rue de l\'envers'))

    def test_order_addresses(self):
        resp = self.testapp.get(self.search_uri, params={'searchText': 'moutier, chemin de graitery', 'type': 'locations'}, status=200)
        self.failUnless(resp.content_type == 'application/json')
        self.failUnless(resp.json['results'][0]['attrs']['detail'] == 'moutier, chemin de graitery, 1')
        self.failUnless(resp.json['results'][1]['attrs']['detail'] == 'moutier, chemin de graitery, 1a')
        self.failUnless(resp.json['results'][7]['attrs']['detail'] == 'moutier, chemin de graitery, 10')
        self.failUnless(resp.json['results'][8]['attrs']['detail'] == 'moutier, chemin de graitery, 12')
        self.failUnless(resp.json['results'][9]['attrs']['detail'] == 'moutier, chemin de graitery, 12a')

    def test_order_communes_addresses(self):
        resp = self.testapp.get(self.search_uri, params={'searchText': 'cor', 'type': 'locations'}, status=200)
        self.failUnless(resp.content_type == 'application/json')
        self.failUnless(resp.json['results'][0]['attrs']['detail'] == 'corcelles _be_')
        self.failUnless(resp.json['results'][1]['attrs']['detail'] == 'corgemont')
        self.failUnless(resp.json['results'][2]['attrs']['detail'] == 'cormoret')
        self.failUnless(resp.json['results'][3]['attrs']['detail'] == 'cortebert')
        self.failUnless(len(resp.json['results']) == 50)

    def test_search_address_with_letters(self):
        resp = self.testapp.get(self.search_uri, params={'searchText': 'Rue des Oeuches, 86', 'type': 'locations'}, status=200)
        self.failUnless(resp.content_type == 'application/json')

    def test_search_locations_escape_charachters(self):
        resp = self.testapp.get(self.search_uri, params={'searchText': 'la fe', 'type': 'locations'}, status=200)
        self.failUnless(len(resp.json['results']) > 0)

    def test_search_locations_authorized(self):
        self.testapp.extra_environ = {'HTTP_X_SEARCHSERVER_AUTHORIZED': 'true'}
        resp = self.testapp.get(self.search_uri, params={'searchText': 'moutier', 'type': 'locations'}, status=200)
        self.failUnless(resp.content_type == 'application/json')
        self.failUnless('geom_st_box2d' in resp.json['results'][0]['attrs'].keys())

    def test_search_locations_authorized_no_geometry(self):
        params = {'searchText': 'moutier', 'type': 'locations', 'returnGeometry': 'false'}
        resp = self.testapp.get(self.search_uri, params=params,
                                headers=dict(HTTP_X_SEARCHSERVER_AUTHORIZED='true'), status=200)
        self.failUnless(resp.content_type == 'application/json')
        self.failUnless('geom_st_box2d' not in resp.json['results'][0]['attrs'].keys())

    def test_search_locations_one_origin(self):
        params = {'searchText': 'moutier', 'type': 'locations', 'origins': 'communes'}
        resp = self.testapp.get(self.search_uri, params=params, status=200)
        self.failUnless(len(resp.json['results']) == 1)

    def test_search_locations_several_origins(self):
        params = {'searchText': 'moutier', 'type': 'locations', 'origins': 'communes,nomderue'}
        resp = self.testapp.get(self.search_uri, params=params, status=200)
        self.failUnless(len(resp.json['results']) > 1)

    def test_search_locations_bad_origin(self):
        params = {'searchText': 'moutier', 'type': 'locations', 'origins': 'dummy'}
        self.testapp.get(self.search_uri, params=params, status=400)

    @unittest.skip('bbox does not work correctly with sphinx')
    def test_search_locations_with_bbox(self):
        params = {'type': 'locations', 'searchText': 'buechli tegerfelden', 'bbox': '664100,268443,664150,268643'}
        resp = self.testapp.get(self.search_uri, params=params, status=200)
        self.failUnless(resp.json['results'][0]['attrs']['detail'] == 'buechli  5306 tegerfelden 4320 tegerfelden ch ag')
        self.failUnless(len(resp.json['results']) == 1)

    @unittest.skip('bbox does not work correctly with sphinx')
    def test_search_locations_bbox_only(self):
        params = {'type': 'locations', 'bbox': '550000,210000,620000,245000'}
        resp = self.testapp.get(self.search_uri, params=params, status=200)
        self.failUnless(resp.content_type == 'application/json')
        self.failUnless(len(resp.json['results']) > 1)

    def test_search_locations_noparams(self):
        params = {'type': 'locations'}
        self.testapp.get(self.search_uri, params=params, status=400)

    def test_location_ofs(self):
        params = {'searchText': '449', 'type': 'locations'}
        resp = self.testapp.get(self.search_uri, params=params, status=200)
        self.failUnless(len(resp.json['results']) > 0)

    def test_location_ofs_arr(self):
        params = {'searchText': '1449', 'type': 'locations'}
        resp = self.testapp.get(self.search_uri, params=params, status=200)
        self.failUnless(len(resp.json['results']) > 0)

    def test_location_wrong_ofs(self):
        params = {'searchText': '10000000000', 'type': 'locations'}
        resp = self.testapp.get(self.search_uri, params=params, status=200)
        self.failUnless(len(resp.json['results']) == 0)

    def test_locations_search_limit(self):
        params = {'searchText': 'moutier', 'type': 'locations', 'limit': '1'}
        resp = self.testapp.get(self.search_uri, params=params, status=200)
        self.failUnless(len(resp.json['results']) == 1)

    def test_locations_search_wrong_limit(self):
        params = {'searchText': 'moutier', 'type': 'locations', 'limit': '5.5'}
        self.testapp.get(self.search_uri, params=params, status=400)

    def test_search_max_words(self):
        self.testapp.get('/rest/services/all/SearchServer', params={'searchText': 'this is a text with exactly 10 words, should work', 'type': 'locations', 'bbox': '551306.5625,167918.328125,551754.125,168514.625'}, status=200)
        self.testapp.get('/rest/services/all/SearchServer', params={'searchText': 'this is a text with exactly 10 words, should work', 'type': 'layers', 'bbox': '551306.5625,167918.328125,551754.125,168514.625'}, status=200)
        self.testapp.get('/rest/services/all/SearchServer', params={'searchText': 'this is a text with exactly 11 words, should NOT work', 'type': 'locations', 'bbox': '551306.5625,167918.328125,551754.125,168514.625'}, status=400)
        self.testapp.get('/rest/services/all/SearchServer', params={'searchText': 'this is a text with exactly 11 words, should NOT work', 'type': 'layers', 'bbox': '551306.5625,167918.328125,551754.125,168514.625'}, status=400)
