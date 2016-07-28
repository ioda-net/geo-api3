from chsdi.tests.integration import TestsBase
from chsdi.models import registered_features


class TestFeatures(TestsBase):
    def test_get_views(self):
        self.assertTrue(len(registered_features) >= 1)

    def test_relead(self):
        resp = self.testapp.get('/geoportalxyz/features_reload')
        self.assertTrue(resp.json['success'])
        self.assertTrue(len(registered_features) >= 1)
