import os
import json
import unittest
from osgeo import ogr
from mapswipe_workers.definitions import ProjectType


class TestGeometryValidation(unittest.TestCase):
    def test_multiple_geom_validation(self):
        # pre steps for outputting result of function
        self.test_dir = os.path.dirname(os.path.abspath(__file__))
        with open(
            os.path.join(self.test_dir, "fixtures/completeness/projectDraft.json")
        ) as json_file:
            project_draft = json.load(json_file)
            self.project_type = project_draft["projectType"]
            self.project = ProjectType(self.project_type).constructor(project_draft)

        # prepare data that is expected
        path = os.path.join(
            self.test_dir, "fixtures/completeness/multiplePolygons.geojson"
        )
        driver = ogr.GetDriverByName("GeoJSON")
        data_source = driver.Open(path, 0)

        self.wkt_geometries_expected = []
        # Get the data layer
        layer = data_source.GetLayer()
        for feature in layer:
            feat_geom = feature.GetGeometryRef()
            self.wkt_geometries_expected.append(feat_geom.ExportToWkt())

        # results coming from the function
        self.wkt = self.project.validate_geometries()
        # Test that sequence first contains the same elements as second
        self.assertCountEqual(self.wkt, self.wkt_geometries_expected)

    def test_single_geom_validation(self):
        # pre steps for outputting result of function
        self.test_dir = os.path.dirname(os.path.abspath(__file__))
        with open(
            os.path.join(
                self.test_dir, "fixtures/completeness/projectDraft_single.json"
            )
        ) as json_file:
            project_draft = json.load(json_file)
            self.project_type = project_draft["projectType"]
            self.project = ProjectType(self.project_type).constructor(project_draft)

        # prepare data that is expected
        path = os.path.join(
            self.test_dir, "fixtures/completeness/single_polygon.geojson"
        )
        driver = ogr.GetDriverByName("GeoJSON")
        datasource = driver.Open(path, 0)

        self.wkt_geometries_expected = []
        # Get the data layer
        layer = datasource.GetLayer()
        for feature in layer:
            feat_geom = feature.GetGeometryRef()
            self.wkt_geometries_expected.append(feat_geom.ExportToWkt())

        # results coming from the function
        self.wkt = self.project.validate_geometries()
        # Test that sequence first contains the same elements as second
        self.assertCountEqual(self.wkt, self.wkt_geometries_expected)


if __name__ == "__main__":
    unittest.main()
