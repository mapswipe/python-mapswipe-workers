import unittest


class TestArchiveProject(unittest.TestCase):
    def test_osgeo_installation(self):
        try:
            from osgeo import ogr, osr, gdal
        except ModuleNotFoundError:
            self.fail()


if __name__ == "__main__":
    unittest.main()
