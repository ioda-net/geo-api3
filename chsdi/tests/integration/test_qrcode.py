# -*- coding: utf-8 -*-

from chsdi.tests.integration import TestsBase


class TestQRCodeView(TestsBase):

    def test_qrcode(self):
        allowed_hosts = self.settings['shortener.allowed_domains'].split(',')
        allowed_host = allowed_hosts[0].strip()
        allowed_url = 'http://{}/e83c57af1'.format(allowed_host)
        resp = self.testapp.get('/qrcodegenerator', params={'url': allowed_url}, status=200)
        self.failUnless(resp.content_type == 'image/png')

    def test_qrcode_badurl(self):
        self.testapp.get('/qrcodegenerator', params={'url': 'http://dummy.com'}, status=400)
