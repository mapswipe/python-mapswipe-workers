import unittest


class TestArchiveProject(unittest.TestCase):
    def test_gdal_installation(self):
        try:
            from osgeo import gdal

            self.assertIsNotNone(gdal)
        except ModuleNotFoundError:
            self.assertIsNotNone(gdal)


if __name__ == "__main__":
    unittest.main()
