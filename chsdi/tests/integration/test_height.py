from chsdi.tests.integration import TestsBase


class TestHeightView(TestsBase):

    def setUp(self):
        super().setUp()
        self.headers = {}

    def test_height_nan(self):
        resp = self.testapp.get(
            '/rest/services/height',
            params={'easting': 'NaN', 'northing': '200000.1'},
            headers=self.headers,
            status=400)
        resp.mustcontain('Please provide numerical values for the parameter \'easting\'/\'lon\'')
        resp = self.testapp.get(
            '/rest/services/height',
            params={'easting': '600000', 'northing': 'NaN'},
            headers=self.headers,
            status=400)
        resp.mustcontain('Please provide numerical values for the parameter \'northing\'/\'lat\'')

    def test_height_wrong_lon_value(self):
        resp = self.testapp.get(
            '/rest/services/height',
            params={'lon': 'toto', 'northing': '200000'},
            headers=self.headers,
            status=400)
        resp.mustcontain("Please provide numerical values")

    def test_height_wrong_lat_value(self):
        resp = self.testapp.get(
            '/rest/services/height',
            params={'lon': '600000', 'northing': 'toto'},
            headers=self.headers,
            status=400)
        resp.mustcontain("Please provide numerical values")

    def test_height_miss_northing(self):
        resp = self.testapp.get(
            '/rest/services/height',
            params={'easting': '600000'},
            headers=self.headers,
            status=400)
        resp.mustcontain("Missing parameter 'norhting'/'lat'")

    def test_height_miss_easting(self):
        resp = self.testapp.get(
            '/rest/services/height',
            params={'northing': '200000'},
            headers=self.headers,
            status=400)
        resp.mustcontain("Missing parameter 'easting'/'lon'")
