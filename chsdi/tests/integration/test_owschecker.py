from chsdi.tests.integration import TestsBase
from nose.plugins.capture import Capture


class TestOwsChecker(TestsBase):

    def setUp(self):
        super(TestOwsChecker, self).setUp()
        self.capture = Capture()
        self.capture.begin()

    def tearDown(self):
        super(TestOwsChecker, self).tearDown()
        del self.capture

    def test_bykvp_no_args(self):
        self.testapp.get('/geoportalxyz/owschecker/bykvp', status=400)

    def test_form(self):
        resp = self.testapp.get('/geoportalxyz/owschecker/form', status=200)
        self.assertTrue(resp.content_type == 'text/html')
        resp.mustcontain("Hint: Don't use tailing")

    def test_bykvp_minimal_wms_request(self):
        base_url = 'http://wms.geo.admin.ch'
        params = {'service': 'WMS', 'base_url': base_url}
        resp = self.testapp.get('/geoportalxyz/owschecker/bykvp', params=params, status=200)
        self.assertTrue(resp.content_type == 'application/json')
        resp.mustcontain("Checked Service: WMS")

    def test_bykvp_minimal_wmts_request(self):
        base_url = 'http://wmts.geo.admin.ch/1.0.0/WMTSCapabilities.xml'
        params = {'service': 'WMTS', 'base_url': base_url}
        resp = self.testapp.get('/geoportalxyz/owschecker/bykvp', params=params, status=200)
        self.assertTrue(resp.content_type == 'application/json')
        resp.mustcontain("Checked Service: WMTS")

    def test_bykvp_minimal_wfs_request(self):
        base_url = 'http://wfs.geo.admin.ch'
        params = {'service': 'WFS', 'base_url': base_url}
        resp = self.testapp.get('/geoportalxyz/owschecker/bykvp', params=params, status=200)
        self.assertTrue(resp.content_type == 'application/json')
        resp.mustcontain("Checked Service: WFS")

    def test_form_minimal_wms_request(self):
        base_url = 'http://wms.geo.admin.ch'
        params = {'service': 'WMS', 'base_url': base_url}
        resp = self.testapp.get('/geoportalxyz/owschecker/form', params=params, status=200)
        self.assertTrue(resp.content_type == 'text/html')
        resp.mustcontain("Checked Service: WMS")
