import unittest


class TestArchiveProject(unittest.TestCase):
    def test_osgeo_installation(self):
        try:
            from osgeo import gdal, ogr, osr  # noqa: F401
        except ModuleNotFoundError:
            self.fail("GDAL is not installed")

    def test_osgeo_version(self):
        from osgeo import gdal, ogr, osr  # noqa: F401

        version_num = int(gdal.VersionInfo("VERSION_NUM"))
        if version_num < 3000000:
            self.fail("GDAL version is not >= 3.0")


if __name__ == "__main__":
    unittest.main()
