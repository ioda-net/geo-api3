# -*- coding: utf-8 -*-

import unittest

from chsdi.tests.integration import TestsBase


class TestOGCproxyView(TestsBase):

    def setUp(self):
        super(TestOGCproxyView, self).setUp()
        self.headers = {'X-SearchServer-Authorized': 'true'}

    @unittest.skip('We disabled the need for X-SearchServer-Authorized')
    def test_proxy_forbidden(self):
        params = {'url': 'http://www.geo.admin.ch/'}
        self.testapp.get('/ogcproxy', params=params, status=403)

    def test_proxy_authorized(self):
        params = {'url': 'http://www.geo.admin.ch/'}
        resp = self.testapp.get('/ogcproxy', params=params, headers=self.headers, status=200)
        self.failUnless(resp.content_type == 'text/html')
        resp.mustcontain('Bundesgeoportal')

    def test_proxy_no_url(self):
        self.testapp.get('/ogcproxy', headers=self.headers, status=400)
