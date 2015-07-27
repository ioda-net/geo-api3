from unittest import TestCase
from pyramid import testing
from webtest import TestApp
import toml


class TestsBase(TestCase):

    def setUp(self):
        from pyramid.paster import get_app
        with open('config.toml', 'r') as test_config_file:
            self.config = toml.load(test_config_file)
            self.test_config = self.config['tests']
        app = get_app('development.ini')
        self.testapp = TestApp(app)
        self.settings = self.testapp.app.registry.settings
        self.default_lang = self.test_config['default_lang']
        self.langs = self.test_config['lang_list']
        self.topic_id = self.test_config['topic_id']
        self.topics_list = self.test_config['topics_list']
        self.layer_id = self.test_config['layer_id']
        self.layers_list = self.test_config['layers_list']

    def tearDown(self):
        testing.tearDown()
        del self.testapp
