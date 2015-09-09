from chsdi.tests.integration import TestsBase


class TestHeightView(TestsBase):

    def setUp(self):
        super().setUp()

    def test_height_outside(self):
        params = {'easting': '600000.1', 'northing': '200000.1'}
        resp = self.testapp.get('/rest/services/height', params=params, status=200)
        self.failUnless(resp.content_type == 'application/json')
        self.failUnless(resp.json['height'] == '')

    def test_height_valid(self):
        params = {'easting': '594171', 'northing': '236290'}
        resp = self.testapp.get('/rest/services/height', params=params, status=200)
        self.failUnless(resp.content_type == 'application/json')
        self.failUnless(resp.json['height'])

    def test_height_valid_with_lonlat(self):
        params = {'lon': '594171', 'lat': '236290'}
        resp = self.testapp.get('/rest/services/height', params=params, status=200)
        self.failUnless(resp.content_type == 'application/json')
        self.failUnless(resp.json['height'])

    def test_height_wrong_elevation_model(self):
        params = {'easting': '600000', 'northing': '200000', 'elevationModel': 'TOTO'}
        resp = self.testapp.get('/rest/services/height', params=params, status=400)
        resp.mustcontain("Please provide a valid name for the elevation")

    def test_height_wrong_lon_value(self):
        params = {'lon': 'toto', 'northing': '200000'}
        resp = self.testapp.get('/rest/services/height', params=params, status=400)
        resp.mustcontain("Please provide numerical values")

    def test_height_wrong_lat_value(self):
        params = {'lon': '600000', 'northing': 'toto'}
        resp = self.testapp.get('/rest/services/height', params=params, status=400)
        resp.mustcontain("Please provide numerical values")

    def test_height_with_callback_valid(self):
        params = {'easting': '600000', 'northing': '200000', 'callback': 'callback'}
        resp = self.testapp.get('/rest/services/height', params=params, status=200)
        self.failUnless(resp.content_type == 'application/javascript')
        resp.mustcontain('callback({')

    def test_height_miss_northing(self):
        params = {'easting': '600000'}
        resp = self.testapp.get('/rest/services/height', params=params, status=400)
        resp.mustcontain("Missing parameter 'norhting'/'lat'")

    def test_height_miss_easting(self):
        params = {'northing': '200000'}
        resp = self.testapp.get('/rest/services/height', params=params, status=400)
        resp.mustcontain("Missing parameter 'easting'/'lon'")
