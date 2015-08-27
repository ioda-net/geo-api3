from chsdi.tests.integration import TestsBase


class TestSearchServiceView(TestsBase):
    def test_bbox_nan(self):
        params = {
            'searchText': 'rue des berges',
            'type': 'locations',
            'bbox': '551306.5625,NaN,551754.125,168514.625'
        }
        resp = self.testapp.get('/rest/services/inspire/SearchServer', params=params, status=400)
        resp.mustcontain('Please provide numerical values for the parameter bbox')
