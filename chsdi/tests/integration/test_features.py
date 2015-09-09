from chsdi.tests.integration import TestsBase
from chsdi.models import registered_features


class TestFeatures(TestsBase):
    def test_get_views(self):
        self.failUnless(len(registered_features) > 1)

    def test_relead(self):
        resp = self.testapp.get('/features_reload')
        self.failUnless(resp.json['success'] == True)
        self.failUnless(len(registered_features) > 1)
