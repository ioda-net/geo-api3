from unittest import TestCase
from pyramid import testing
from webtest import TestApp
import toml


class TestsBase(TestCase):

    def setUp(self):
        from pyramid.paster import get_app
        with open('config.toml', 'r') as config_file:
            full_config = toml.load(config_file)
            self.config = full_config['tests']
        app = get_app('development.ini')
        self.testapp = TestApp(app)
        self.settings = self.testapp.app.registry.settings
        self.default_lang = self.config['default_lang']
        self.langs = self.config['lang_list']
        self.topic_id = self.config['topic_id']
        self.topics_list = self.config['topics_list']
        self.layer_id = self.config['layer_id']
        self.layers_list = self.config['layers_list']

    def tearDown(self):
        testing.tearDown()
        del self.testapp
