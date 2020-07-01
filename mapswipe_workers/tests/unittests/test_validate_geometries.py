import os
import json
import unittest
from osgeo import ogr
from mapswipe_workers.definitions import ProjectType


def create_project(path):
    # pre steps for outputting result of function
    test_dir = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(test_dir, path)) as json_file:
        project_draft = json.load(json_file)
        project_type = project_draft["projectType"]
        project = ProjectType(project_type).constructor(project_draft)

    return project


class TestGeometryValidation(unittest.TestCase):
    def test_multiple_geom_validation(self):
        path = "fixtures/completeness/projectDraft.json"
        test_dir = os.path.dirname(os.path.abspath(__file__))
        project = create_project(path)
        # prepare data that is expected
        path = os.path.join(test_dir, "fixtures/completeness/multiplePolygons.geojson")
        driver = ogr.GetDriverByName("GeoJSON")
        data_source = driver.Open(path, 0)

        wkt_geometries_expected = []
        # Get the data layer
        layer = data_source.GetLayer()
        for feature in layer:
            feat_geom = feature.GetGeometryRef()
            wkt_geometries_expected.append(feat_geom.ExportToWkt())

        # results coming from the validate geometries function
        wkt = project.validate_geometries()
        # Test that sequence first contains the same elements as second
        self.assertCountEqual(wkt, wkt_geometries_expected)

    def test_single_geom_validation(self):
        path = "fixtures/completeness/projectDraft_single.json"
        test_dir = os.path.dirname(os.path.abspath(__file__))
        project = create_project(path)

        # prepare data that is expected
        path = os.path.join(test_dir, "fixtures/completeness/single_polygon.geojson")
        driver = ogr.GetDriverByName("GeoJSON")
        datasource = driver.Open(path, 0)

        wkt_geometries_expected = []
        # Get the data layer
        layer = datasource.GetLayer()
        for feature in layer:
            feat_geom = feature.GetGeometryRef()
            wkt_geometries_expected.append(feat_geom.ExportToWkt())

        # results coming from the validate_geometries function
        wkt = project.validate_geometries()
        # Test that sequence first contains the same elements as second
        self.assertCountEqual(wkt, wkt_geometries_expected)


if __name__ == "__main__":

    unittest.main()
