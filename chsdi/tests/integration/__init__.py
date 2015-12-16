import toml

from pyramid import testing
from pyramid.paster import get_app
from unittest import TestCase
from webtest import TestApp


class TestsBase(TestCase):

    def setUp(self):
        with open('config/config.toml', 'r') as test_config_file:
            self.config = toml.load(test_config_file)
            self.test_config = self.config['tests']
        app = get_app('development.ini')
        self.testapp = TestApp(app)
        self.layer_id = self.test_config['layer_id']

    def tearDown(self):
        testing.tearDown()
        del self.testapp
