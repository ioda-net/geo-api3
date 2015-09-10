import re
import time

from pyramid.httpexceptions import HTTPBadRequest

from chsdi.lib.url_shortener import check_url
from chsdi.tests.integration import TestsBase


class TestShortener(TestsBase):
    def setUp(self):
        super().setUp()
        self.allowed_domain = self.config['template']['shortener']['allowed_domains'].split(',')[0]
        self.base_url = 'http://{}/'.format(self.allowed_domain)
        # Link is only added if not in database. So we create a random one each time.
        location = self.base_url + str(int(time.time()))
        self.resp = self.testapp.get(
            '/shorten.json',
            params={'url': location},
            status=200)
        self.shorturl = self.resp.json['shorturl']
        self.api_host = self.config['template']['debug']['host']

    def test_check_url(self):
        url = None
        config = {'shortener.allowed_hosts': 'admin.ch,swisstopo.ch,bgdi.ch'}
        try:
            check_url(url, config)
        except Exception as e:
            self.assertTrue(isinstance(e, HTTPBadRequest))

        url = 'dummy'
        try:
            check_url(url, config)
        except Exception as e:
            self.assertTrue(isinstance(e, HTTPBadRequest))

        url = 'http://dummy.com'
        try:
            check_url(url, config)
        except Exception as e:
            self.assertTrue(isinstance(e, HTTPBadRequest))

        url = 'http://admin.ch'
        self.assertEqual(url, check_url(url, config))

    def test_no_url(self):
        self.testapp.get('/shorten.json', status=400)

    def test_get_non_existant(self):
        self.testapp.get('/shorten/dummy', status=400)

    def test_create_short_link(self):
        regexp = 'https?://' + self.api_host + '/shorten/[0-9a-f]{10}'
        self.assertTrue(re.match(regexp, self.shorturl))

    def test_get_short_link(self):
        self.testapp.get(self.shorturl, status=301)

    def test_too_long(self):
        params = {
            'url': self.base_url + 'a'*2050
        }
        headers = {'origin': self.base_url}
        resp = self.testapp.get(
            '/shorten.json',
            params=params,
            headers=headers,
            status=200)
        resp = self.testapp.get(resp.json['shorturl'], status=301)
        self.assertTrue(resp.headers['location'] == self.base_url)
