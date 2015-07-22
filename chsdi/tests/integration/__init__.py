from unittest import TestCase
from pyramid import testing
from webtest import TestApp


class TestsBase(TestCase):

    def setUp(self):
        from pyramid.paster import get_app
        app = get_app('development.ini')
        self.testapp = TestApp(app)
        self.settings = self.testapp.app.registry.settings
        self.default_lang = self.settings['default_lang']
        self.langs = [lang.strip() for lang in self.settings['langs_list'].split(',')]
        self.topic_id = self.settings['topic_id']
        self.topics_list = [topic.strip() for topic in self.settings['topics_list'].split(',')]
        self.layer_id = self.settings['layer_id']
        self.layers_list = [layer.strip() for layer in self.settings['layers_list'].split(',')]

    def tearDown(self):
        testing.tearDown()
        del self.testapp
