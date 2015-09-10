from chsdi.tests.integration import TestsBase


class TestOGCproxyView(TestsBase):

    def setUp(self):
        super().setUp()

    def test_proxy_authorized(self):
        params = {'url': 'http://www.geo.admin.ch/'}
        resp = self.testapp.get('/ogcproxy', params=params, status=200)
        self.assertTrue(resp.content_type == 'text/html')
        resp.mustcontain('Bundesgeoportal')

    def test_proxy_kmz(self):
        params = {'url': 'http://dl.google.com/developers/maps/buffetthawaiitour.kmz'}
        resp = self.testapp.get('/ogcproxy', params=params, status=200)
        self.assertTrue(resp.content_type == 'application/vnd.google-earth.kml+xml')
        resp.mustcontain('Jimmy Buffett Hawaii Tour')

    def test_proxy_no_url(self):
        self.testapp.get('/ogcproxy', status=400)
