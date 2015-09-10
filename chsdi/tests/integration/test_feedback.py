from collections import OrderedDict
from chsdi.tests.integration import TestsBase


class TestFeedback(TestsBase):
    def setUp(self):
        super().setUp()
        self.payload = OrderedDict()
        self.payload['email'] = 'vador@ioda.net'
        self.payload['feedback'] = 'Ça ne fonctionne pas'
        self.payload['ua'] = 'User Agent'
        self.payload['permalink'] = 'http://geojb.ch'
        self.empty_kml = ''
        self.kml = '<kml></kml>'
        self.file = ('attachment', 'test.txt', 'Cocuou'.encode('utf-8'))

    def test_send_mail(self):
        resp = self.testapp.post('/feedback', params=self.payload, status=200)
        self.assertTrue(resp.json['success'])

    def test_send_mail_with_empty_kml(self):
        self.payload['kml'] = self.empty_kml
        resp = self.testapp.post(
            '/feedback',
            params=self.payload,
            status=200)
        self.assertTrue(resp.json['success'])

    def test_send_mail_with_kml(self):
        self.payload['kml'] = self.kml
        resp = self.testapp.post(
            '/feedback',
            params=self.payload,
            status=200)
        self.assertTrue(resp.json['success'])

    def test_send_mail_with_file(self):
        resp = self.testapp.post(
            '/feedback',
            params=self.payload,
            upload_files=[self.file],
            status=200)
        self.assertTrue(resp.json['success'])

    def test_send_mail_all(self):
        self.payload['kml'] = self.kml
        resp = self.testapp.post(
            '/feedback',
            params=self.payload,
            upload_files=[self.file],
            status=200)
        self.assertTrue(resp.json['success'])
