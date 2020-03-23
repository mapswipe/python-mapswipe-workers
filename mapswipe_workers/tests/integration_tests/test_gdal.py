import unittest


class TestArchiveProject(unittest.TestCase):
    def test_gdal_installation(self):
        try:
            from osgeo import ogr, osr, gdal
        except ModuleNotFoundError:
            pass
        self.assertIsNotNone(ogr)
        self.assertIsNotNone(osr)
        self.assertIsNotNone(gdal)


if __name__ == "__main__":
    unittest.main()
