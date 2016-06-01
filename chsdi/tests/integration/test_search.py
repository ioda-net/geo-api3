# -*- coding: utf-8 -*-

from chsdi.tests.integration import TestsBase


class TestSearchServiceView(TestsBase):

    def test_no_type(self):
        self.testapp.get(
            '/geoportalxyz/rest/services/SearchServer',
            params={'searchText': 'ga'},
            status=400
        )

    def test_unaccepted_type(self):
        resp = self.testapp.get(
            '/geoportalxyz/rest/services/SearchServer',
            params={'searchText': 'ga', 'type': 'unaccepted'},
            status=400
        )
        acceptedTypes = ['locations', 'locations_preview', 'layers', 'featuresearch']
        resp.mustcontain(
            "The type parameter you provided is not valid. Possible values are %s" %
            (', '.join(acceptedTypes))
        )

    def test_searchtext_none_value_layers(self):
        resp = self.testapp.get(
            '/geoportalxyz/rest/services/SearchServer',
            params={'type': 'layers'},
            status=400
        )
        resp.mustcontain("Please provide a search text")

    def test_searchtext_empty_string_layers(self):
        resp = self.testapp.get(
            '/geoportalxyz/rest/services/SearchServer',
            params={'type': 'layers', 'searchText': '  '},
            status=400
        )
        resp.mustcontain("Please provide a search text")

    def test_searchtext_none_locations(self):
        resp = self.testapp.get(
            '/geoportalxyz/rest/services/SearchServer',
            params={'type': 'locations'},
            status=400
        )
        resp.mustcontain("Please provide a search text")

    def test_searchtext_none_value_locations(self):
        resp = self.testapp.get(
            '/geoportalxyz/rest/services/SearchServer',
            params={'type': 'locations', 'searchText': '  '},
            status=400
        )
        resp.mustcontain("Please provide a search text")

    def test_bbox_wrong_number_coordinates(self):
        resp = self.testapp.get(
            '/geoportalxyz/rest/services/SearchServer',
            params={
                'searchText': 'rue des berges',
                'type': 'locations',
                'bbox': '551306.5625,551754.125,168514.625'
            },
            status=400
        )
        resp.mustcontain('Please provide 4 coordinates in a comma separated list')

    def test_bbox_check_first_second_coordinates(self):
        resp = self.testapp.get(
            '/geoportalxyz/rest/services/SearchServer',
            params={
                'searchText': 'rue des berges',
                'type': 'locations',
                'bbox': '420000,420010,551754.125,168514.625'
            },
            status=400
        )
        resp.mustcontain('The first coordinate must be higher than the second')

    def test_bbox_check_third_fourth_coordinates(self):
        resp = self.testapp.get(
            '/geoportalxyz/rest/services/SearchServer',
            params={
                'searchText': 'rue des berges',
                'type': 'locations',
                'bbox': '551306.5625,167918.328125,420000,420010'
            },
            status=400
        )
        resp.mustcontain('The third coordinate must be higher than the fourth')

    def test_search_locations_bad_origin(self):
        params = {'searchText': 'vaud', 'type': 'locations', 'origins': 'dummy'}
        self.testapp.get('/geoportalxyz/rest/services/SearchServer', params=params, status=400)

    def test_search_locations_noparams(self):
        params = {'type': 'locations'}
        self.testapp.get('/geoportalxyz/rest/services/SearchServer', params=params, status=400)

    def test_locations_search_wrong_limit(self):
        params = {'searchText': 'chalais', 'type': 'locations', 'limit': '5.5'}
        self.testapp.get('/geoportalxyz/rest/services/SearchServer', params=params, status=400)

    def test_bbox_nan(self):
        resp = self.testapp.get(
            '/geoportalxyz/rest/services/SearchServer',
            params={
                'searchText': 'rue des berges',
                'type': 'locations',
                'bbox': '551306.5625,NaN,551754.125,168514.625'
            },
            status=400
        )
        resp.mustcontain('Please provide numerical values for the parameter bbox')
