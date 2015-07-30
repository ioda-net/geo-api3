from chsdi.tests.integration import TestsBase
from chsdi.models import registered_features


class TestFeatures(TestsBase):
    def test_get_views(self):
        self.failUnless(len(registered_features) > 1)
