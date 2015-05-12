# -*- coding: utf-8 -*-

from unittest import TestCase
from pyramid import testing
from webtest import TestApp


class TestsBase(TestCase):

    def setUp(self):
        from pyramid.paster import get_app
        app = get_app('development.ini')
        self.testapp = TestApp(app)
        self.settings = self.testapp.app.registry.settings
        self.topic_id = self.settings['topic_id']
        self.layer_id = self.settings['layer_id']

    def tearDown(self):
        testing.tearDown()
        del self.testapp
