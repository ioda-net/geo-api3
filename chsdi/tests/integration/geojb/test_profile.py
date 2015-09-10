import json

from chsdi.tests.integration import TestsBase


class TestProfileView(TestsBase):

    def setUp(self):
        super().setUp()

    def test_profile_json_valid(self):
        elevation_model = self.config['template']['raster']['preloaded'][0]
        geom = {
            "type": "LineString",
            "coordinates": [
                [589590.8, 235646.3],
                [589030.8, 235323.8],
                [588558.3, 235456.3]
            ]
        }
        params = {
            'geom': json.dumps(geom),
            'elevationModel': elevation_model
        }
        resp = self.testapp.get('/rest/services/profile.json', params=params, status=200)
        self.assertTrue(resp.content_type == 'application/json')
        self.assertTrue(resp.json[0]['dist'] == 0)
        self.assertTrue(resp.json[0]['alts'][elevation_model] == 874)
        self.assertTrue(resp.json[0]['easting'] == 589590.8)
        self.assertTrue(resp.json[0]['northing'] == 235646.3)

        geom = {
            "type": "LineString",
            "coordinates": [
                [589590.8, 235646.3],
                [589030.8, 235323.8]
            ]
        }
        params = {
            'geom': json.dumps(geom)
        }
        self.testapp.get('/rest/services/profile.json', params=params, status=200)

    def test_profile_json_with_callback_valid(self):
        geom = {
            "type": "LineString",
            "coordinates": [
                [550050, 206550],
                [556950, 204150],
                [561050, 207950]
            ]
        }
        params = {
            'geom': json.dumps(geom),
            'callback': 'callback'
        }
        resp = self.testapp.get('/rest/services/profile.json', params=params, status=200)
        self.assertTrue(resp.content_type == 'application/javascript')
        resp.mustcontain('callback([')

    def test_profile_json_missing_geom(self):
        resp = self.testapp.get('/rest/services/profile.json', status=400)
        resp.mustcontain('Missing parameter geom')

    def test_profile_json_wrong_geom(self):
        params = {'geom': 'toto'}
        resp = self.testapp.get('/rest/services/profile.json', params=params, status=400)
        resp.mustcontain('Error loading geometry in JSON string')

    def test_profile_json_nb_points(self):
        geom = {
            "type": "LineString",
            "coordinates": [
                [550050, 206550],
                [556950, 204150],
                [561050, 207950]
            ]
        }
        params = {
            'geom': json.dumps(geom),
            'nbPoints': '150'
        }
        resp = self.testapp.get('/rest/services/profile.json', params=params, status=200)
        self.assertTrue(resp.content_type == 'application/json')

        geom = {
            "type": "LineString",
            "coordinates": [
                [550050, 206550],
                [556950, 204150],
                [561050, 207950]
            ]
        }
        params = {
            'geom': json.dumps(geom),
            'nbPoints': '1'
        }
        resp = self.testapp.get('/rest/services/profile.json', params=params, status=200)
        self.assertTrue(resp.content_type == 'application/json')

    def test_profile_wrong_line_string(self):
        geom = {
            "type": "LineString",
            "coordinates": []
        }
        params = {
            'geom': json.dumps(geom),
            'nbPoints': '10'
        }
        self.testapp.get('/rest/services/profile.json', params=params, status=400)

        geom = {
            "type": "LineString",
            "coordinates": [[550050, 206550]]
        }
        params = {
            'geom': json.dumps(geom),
            'nbPoints': '10'
        }
        self.testapp.get('/rest/services/profile.json', params=params, status=400)

        geom = {
            "type": "LineString",
            "coordinates": [
                [550050, 206550],
                [550050, 206550]
            ]
        }
        params = {
            'geom': json.dumps(geom),
            'nbPoints': '10'
        }
        self.testapp.get('/rest/services/profile.json', params=params, status=200)

    def test_profile_json_nb_points_wrong(self):
        geom = {
            "type": "LineString",
            "coordinates": [
                [550050, 206550],
                [556950, 204150],
                [561050, 207950]
            ]
        }
        params = {
            'geom': json.dumps(geom),
            'nbPoints': 'toto'
        }
        resp = self.testapp.get('/rest/services/profile.json', params=params, status=400)
        resp.mustcontain("Please provide a numerical value for the parameter 'NbPoints'")

    def test_profile_csv_valid(self):
        geom = {
            "type": "LineString",
            "coordinates": [
                [589590.8, 235646.3],
                [589030.8, 235323.8],
                [588558.3, 235456.3]
            ]
        }
        params = {
            'geom': json.dumps(geom)
            }
        resp = self.testapp.get('/rest/services/profile.csv', params=params, status=200)
        self.assertTrue(resp.content_type == 'text/csv')

    def test_profile_cvs_wrong_geom(self):
        params = {'geom': 'toto'}
        resp = self.testapp.get('/rest/services/profile.csv', params=params, status=400)
        resp.mustcontain('Error loading geometry in JSON string')

    def test_profile_json_invalid_linestring(self):
        geom = {
            "type": "LineString",
            "coordinates": [[550050, 206550]]
        }
        params = {
            'geom': json.dumps(geom)
        }
        resp = self.testapp.get('/rest/services/profile.json', params=params, status=400)
        resp.mustcontain('Invalid Linestring syntax')

    def test_profile_layer(self):
        geom = {
            "type": "LineString",
            "coordinates": [
                [550050, 206550],
                [556950, 204150],
                [561050, 207950]
            ]
        }
        params = {
            'geom': json.dumps(geom),
            'elevationModels': ['MNT50']
        }
        self.testapp.get('/rest/services/profile.json', params=params, status=200)

    def test_profile_wrong_layer(self):
        geom = {
            "type": "LineString",
            "coordinates": [
                [550050, 206550],
                [556950, 204150],
                [561050, 207950]
            ]
        }
        params = {
            'geom': json.dumps(geom),
            'elevationModels': ['toto']
        }
        self.testapp.get('/rest/services/profile.json', params=params, status=400)

    def test_profile_offset(self):
        geom = {
            "type": "LineString",
            "coordinates": [
                [550050, 206550],
                [556950, 204150],
                [561050, 207950]
            ]
        }
        params = {
            'geom': json.dumps(geom),
            'offset': 3
        }
        self.testapp.get('/rest/services/profile.json', params=params, status=200)

    def test_profile_wrong_offset(self):
        geom = {
            "type": "LineString",
            "coordinates": [
                [550050, 206550],
                [556950, 204150],
                [561050, 207950]
            ]
        }
        params = {
            'geom': json.dumps(geom),
            'offset': 'aaa'
        }
        self.testapp.get('/rest/services/profile.json', params=params, status=400)
