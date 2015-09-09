from chsdi.tests.integration import TestsBase


class TestProtocol(TestsBase):
    def test_bad_request(self):
        self.testapp.get('/protocol', status=404)
        self.testapp.get('/protocol/pfp', status=404)
        self.testapp.get('/protocol/pfp/not_an_id', status=404)
        self.testapp.get('/protocol/not_a_type/not_an_id', status=406)

    def test_correct_request_pfp(self):
        resp = self.testapp.get('/protocol/pfp/TOV70', status=200)
        self.failUnless(resp.content_type == 'application/pdf')

    def test_correct_request_pdc(self):
        resp = self.testapp.get('/protocol/pdc/1640_00008871', status=200)
        self.failUnless(resp.content_type == 'application/pdf')

    def test_correct_request_geo(self):
        resp = self.testapp.get('/protocol/geo/PVC1_PIEZO1', status=200)
        self.failUnless(resp.content_type == 'application/pdf')

        resp = self.testapp.get('/protocol/geo/RAI9', status=200)
        self.failUnless(resp.content_type == 'application/pdf')

        resp = self.testapp.get('/protocol/geo/P 2', status=200)
        self.failUnless(resp.content_type == 'application/pdf')

        resp = self.testapp.get('/protocol/geo/D02-FC20', status=200)
        self.failUnless(resp.content_type == 'application/pdf')

        resp = self.testapp.get('/protocol/geo/MS3.0', status=200)
        self.failUnless(resp.content_type == 'application/pdf')
