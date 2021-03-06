from pyramid import testing
from pyramid.paster import get_app
from unittest import TestCase
from webtest import TestApp
from tasks.config import get_git_branch, load_config


class TestsBase(TestCase):

    def setUp(self):
        self.config = load_config(git_branch=get_git_branch())
        self.test_config = self.config['tests']
        app = get_app('development.ini')
        self.testapp = TestApp(app)
        self.layer_id = self.test_config['layer_id']

    def tearDown(self):
        testing.tearDown()
        del self.testapp
