from chsdi.tests.integration import TestsBase


class TestQRCodeView(TestsBase):

    def test_qrcode(self):
        shortener_allowed_domain = self.config['shortener']['allowed_domains'][0]
        allowed_url = 'http://{}/e83c57af1'.format(shortener_allowed_domain)
        resp = self.testapp.get(
            '/geoportalxyz/qrcodegenerator',
            params={'url': allowed_url},
            status=200)
        self.assertTrue(resp.content_type == 'image/png')

    def test_qrcode_badurl(self):
        self.testapp.get(
            '/geoportalxyz/qrcodegenerator',
            params={'url': 'http://dummy.com'},
            status=400)
