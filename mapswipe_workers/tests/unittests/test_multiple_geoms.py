import os
import unittest
from mapswipe_workers.utils import tile_grouping_functions as t
from osgeo import ogr


class TestMultipleGeoms(unittest.TestCase):
    def setUp(self):
        self.test_dir = os.path.dirname(os.path.abspath(__file__))
        self.project_extent_file = os.path.join(
            self.test_dir, "fixtures/completeness/single_polygon.geojson"
        )

    def test_get_horizontal_slice(self):
        extent, geomcol = t.get_geometry_from_file(self.project_extent_file)

        horizontal_slices_expected = os.path.join(
            self.test_dir, "fixtures/completeness/horizontal_slices_expected.geojson"
        )
        # read geojson file with expected geometry
        driver = ogr.GetDriverByName("GeoJSON")
        datasource = driver.Open(horizontal_slices_expected, 0)
        layer = datasource.GetLayer()
        wkt_before = []

        # transform geometries into wkt geometries
        for feature in layer:
            feat_geom = feature.GetGeometryRef()
            wkt_geometry = feat_geom.ExportToWkt()
            wkt_before.append(wkt_geometry)

        # check if geometries are the same as before (before modification)
        slices_info = t.get_horizontal_slice(extent, geomcol, 18)
        geomcol = slices_info["slice_collection"]

        wkt_after = []
        for feature in geomcol:
            wkt_geometry = feature.ExportToWkt()
            wkt_after.append(wkt_geometry)

        self.assertCountEqual(wkt_before, wkt_after)


if __name__ == "__main__":
    unittest.main()
