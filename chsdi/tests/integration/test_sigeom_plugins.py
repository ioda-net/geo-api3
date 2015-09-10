from chsdi.tests.integration import TestsBase


class TestCommunes(TestsBase):
    def setUp(self):
        super().setUp()

    def test_no_coords(self):
        self.testapp.get('/communes', status=400)
        self.testapp.get('/communes?x=0', status=400)
        self.testapp.get('/communes?y=0', status=400)

    def test_no_result(self):
        resp = self.testapp.get('/communes?x=-1&y=-1', status=200)
        self.assertTrue(resp.json == {})

    def test_commune(self):
        resp = self.testapp.get('/communes?x=594171&y=236290', status=200)
        self.assertTrue(resp.json['commune'] == 'Moutier')
