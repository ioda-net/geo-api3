import os
from urllib.parse import quote_plus
from chsdi.tests.integration import TestsBase


WRONG_CONTENT_TYPE = 'nasty type'


VALID_KML = '''<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
  <Placemark>
    <name>Simple placemark</name>
    <description>Attached to the ground. Intelligently places itself
       at the height of the underlying terrain.</description>
    <Point>
      <coordinates>-122.0822035425683,37.42228990140251,0</coordinates>
    </Point>
  </Placemark>
</kml>'''

URLENCODED_KML = quote_plus('''<kml xmlns="http://www.opengis.net/kml/2.2"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xsi:schemaLocation="http://www.opengis.net/kml/2.2
        https://developers.google.com/kml/schema/kml22gx.xsd">
<Document>
    <name>Drawing</name>
    <Placemark>
        <Style>
            <IconStyle>
                <scale>0.25</scale>
                <Icon>
                    <href>
                        https://mf-geoadmin3.dev.bgdi.ch/ltjeg/1432804593/img/maki/circle-24@2x.png
                    </href>
                    <gx:w xmlns:gx="http://www.google.com/kml/ext/2.2">48</gx:w>
                    <gx:h xmlns:gx="http://www.google.com/kml/ext/2.2">48</gx:h>
                </Icon><hotSpot x="24" y="24" xunits="pixels" yunits="pixels" />
            </IconStyle>
        </Style>
        <Point><coordinates>6.724650291365927,46.804920188214076</coordinates></Point>
    </Placemark>
    <Placemark>
        <Style>
            <IconStyle>
                <scale>0.25</scale>
                <Icon>
                    <href>
                        https://mf-geoadmin3.dev.bgdi.ch/ltjeg/1432804593/img/maki/circle-24@2x.png
                    </href>
                    <gx:w xmlns:gx="http://www.google.com/kml/ext/2.2">48</gx:w>
                    <gx:h xmlns:gx="http://www.google.com/kml/ext/2.2">48</gx:h>
                </Icon>
                <hotSpot x="24" y="24" xunits="pixels" yunits="pixels" />
            </IconStyle>
        </Style>
        <Point><coordinates>6.728334379750007,46.52607115587267</coordinates></Point>
    </Placemark>
</Document></kml>
'''.replace('\n', ''))

NOT_WELL_FORMED_KML = '''<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
    <name>Simple placemark</name
    <description>Attached to the ground. Intelligently places itself
       at the height of the underlying terrain.</description>
      <coordinates>-122.0822035425683,37.42228990140251,0</coordinates>
    </Point>
  <Placemark>
</kml>'''


class TestFileView(TestsBase):

    def setUp(self):
        super().setUp()
        self.headers = {'Content-Type': 'application/vnd.google-earth.kml+xml'}

    def test_options(self):
        resp = self.testapp.options('/files', status=200)
        self.assertEqual(resp.headers['Access-Control-Allow-Methods'], 'POST,GET,DELETE,OPTIONS')
        self.assertEqual(resp.headers['Access-Control-Allow-Credentials'], 'true')

        resp = self.testapp.options('/files/toto', status=200)
        self.assertEqual(resp.headers['Access-Control-Allow-Methods'], 'POST,GET,DELETE,OPTIONS')
        self.assertEqual(resp.headers['Access-Control-Allow-Credentials'], 'true')

    def test_create_get_kml(self):
        resp = self.testapp.post('/files', VALID_KML, headers=self.headers, status=200)
        self.assertIn('adminId', resp.json)
        self.assertIn('fileId', resp.json)

        # Get with admin id
        admin_id = resp.json['adminId']
        resp = self.testapp.get('/files/{}'.format(admin_id), status=200)
        self.assertIn('fileId', resp.json)

        # Get with file id
        file_id = resp.json['fileId']
        resp = self.testapp.get('/files/{}'.format(file_id), status=200)
        self.assertIn('Content-Type', resp.headers)
        self.assertEqual(
            'application/vnd.google-earth.kml+xml; charset=UTF-8',
            resp.headers['Content-Type'])
        self.assertEqual(resp.body.decode('utf-8'), VALID_KML)

    def test_inexistant_id(self):
        self.testapp.get('/files/toto', status=404)
        self.testapp.delete('/files/toto', status=404)

    def test_file_invalid_content_type(self):
        headers = {'Content-Type': WRONG_CONTENT_TYPE}
        self.testapp.post('/files', VALID_KML, headers=headers, status=415)

    def test_file_not_well_formed_kml(self):
        self.testapp.post('/files', NOT_WELL_FORMED_KML, headers=self.headers, status=415)

    def test_update_kml(self):
        resp = self.testapp.post('/files', VALID_KML, headers=self.headers, status=200)
        admin_id = resp.json['adminId']

        url = '/files/%s' % admin_id
        resp = self.testapp.post(url, VALID_KML, headers=self.headers, status=200)
        self.assertTrue(resp.json['status'], 'updated')
        self.assertEqual(admin_id, resp.json['adminId'])

    def test_forked_kml(self):
        resp = self.testapp.post('/files', VALID_KML, headers=self.headers, status=200)
        admin_id = resp.json['adminId']
        file_id = resp.json['fileId']

        url = '/files/%s' % file_id
        resp = self.testapp.post(url, VALID_KML, headers=self.headers, status=200)
        self.assertEqual(resp.json['status'], 'copied')
        self.assertNotEqual(admin_id, resp.json['adminId'])
        self.assertNotEqual(file_id, resp.json['fileId'])

    def test_delete_kml(self):
        resp = self.testapp.post('/files', VALID_KML, headers=self.headers, status=200)
        admin_id = resp.json['adminId']
        file_id = resp.json['fileId']

        # delete with file_id
        resp = self.testapp.delete('/files/%s' % file_id, headers=self.headers, status=401)

        # Delete with admin_id
        resp = self.testapp.delete('/files/%s' % admin_id, headers=self.headers, status=200)
        self.assertTrue(resp.json['success'])

        # Delete non existent file (this is not an admin_id os this is not authorized)
        url = '/files/%s' % 'this-file-is-nothing'
        resp = self.testapp.delete(url, headers=self.headers, status=404)

    def test_file_too_big_kml(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        with open(os.path.join(current_dir, 'big.kml')) as f:
            data = f.read()
        resp = self.testapp.post('/files', data, headers=self.headers, status=413)
        self.assertIn('File size exceed', resp.body.decode('utf-8'))

    def test_update_copy_kml(self):
        # First request, to get ids
        resp = self.testapp.post('/files', VALID_KML, headers=self.headers, status=200)
        admin_id = resp.json['adminId']
        file_id = resp.json['fileId']

        # get file
        resp = self.testapp.get('/files/%s' % file_id, headers=self.headers, status=200)
        orig_data = resp.body
        self.assertEqual(orig_data, VALID_KML.encode('utf-8'))

        # update with file_id, should copy
        new_content = VALID_KML.replace('Simple placemark', 'Not so simple placemark')
        url = '/files/%s' % file_id
        resp = self.testapp.post(url, new_content, headers=self.headers, status=200)
        new_admin_id = resp.json['adminId']
        new_file_id = resp.json['fileId']
        modified_content = resp.body

        self.assertNotEqual(admin_id, new_admin_id)
        self.assertNotEqual(file_id, new_file_id)

        # re-get first file
        resp = self.testapp.get('/files/%s' % file_id, headers=self.headers, status=200)
        new_content = resp.body

        self.assertEqual(new_content, VALID_KML.encode('utf-8'))
        self.assertNotEqual(new_content, modified_content)

    def test_file_ie9_fix(self):
        # No cotent-type should normally result in error
        self.testapp.post('/files', URLENCODED_KML, headers={}, status=415)
        # Having IE9 user-agent makes it working again
        self.testapp.post('/files', URLENCODED_KML, headers={'User-Agent': 'MSIE 9.0'}, status=200)
