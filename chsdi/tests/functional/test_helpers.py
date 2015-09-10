import unittest

from chsdi.lib.helpers import transformCoordinate


class TestHelpers(unittest.TestCase):

    def test_transformCoordinate(self):
        from osgeo.ogr import Geometry
        wkt = 'POINT (7.37840 45.91616)'
        srid_from = 4326
        srid_to = 21781
        wkt_21781 = transformCoordinate(wkt, srid_from, srid_to)
        self.assertTrue(isinstance(wkt_21781, Geometry))
        self.assertEqual(int(wkt_21781.GetX()), 595324)
        self.assertEqual(int(wkt_21781.GetY()), 84952)
