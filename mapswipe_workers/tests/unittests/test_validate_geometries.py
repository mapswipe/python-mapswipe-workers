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
        path = "fixtures/completeness/projectDraft_overlappingGeom.json"
        test_dir = os.path.dirname(os.path.abspath(__file__))
        project = create_project(path)

        # prepare data that is expected
        path = os.path.join(test_dir, "fixtures/completeness/overlappingGeoms.geojson")
        driver = ogr.GetDriverByName("GeoJSON")
        datasource = driver.Open(path, 0)

        geometry_collection = ogr.Geometry(ogr.wkbMultiPolygon)
        # Get the data layer
        layer = datasource.GetLayer()
        for feature in layer:
            feat_geom = feature.GetGeometryRef()
            geom_name = feat_geom.GetGeometryName()
            # add geometry to geometry collection
            # check if input geom is multipolygon or polygon
            if geom_name == "MULTIPOLYGON":
                for multi in feat_geom:
                    geometry_collection.AddGeometry(multi)
                # apply union function if multiple geoms of polygons overlap
                dissolved_geometry = geometry_collection.UnionCascaded()
                wkt_geometry_collection = dissolved_geometry.ExportToWkt()
            if geom_name == "POLYGON":
                geometry_collection.AddGeometry(feat_geom)
                wkt_geometry_collection = geometry_collection.ExportToWkt()

        # results coming from the validate_geometries function
        wkt = project.validate_geometries()
        # Test that sequence first contains the same elements as second
        self.assertCountEqual(wkt, wkt_geometry_collection)

    def test_single_geom_validation(self):
        path = "fixtures/completeness/projectDraft_single.json"
        test_dir = os.path.dirname(os.path.abspath(__file__))
        project = create_project(path)

        # prepare data that is expected
        path = os.path.join(test_dir, "fixtures/completeness/single_polygon.geojson")
        driver = ogr.GetDriverByName("GeoJSON")
        datasource = driver.Open(path, 0)

        geometry_collection = ogr.Geometry(ogr.wkbMultiPolygon)
        # Get the data layer
        layer = datasource.GetLayer()
        for feature in layer:
            feat_geom = feature.GetGeometryRef()
            geom_name = feat_geom.GetGeometryName()
            # add geometry to geometry collection
            if geom_name == "MULTIPOLYGON":
                for multi in feat_geom:
                    geometry_collection.AddGeometry(multi)
            if geom_name == "POLYGON":
                geometry_collection.AddGeometry(feat_geom)

        dissolved_geometry = geometry_collection.UnionCascaded()
        wkt_geometry_collection = dissolved_geometry.ExportToWkt()

        # results coming from the validate_geometries function
        wkt = project.validate_geometries()
        # Test that sequence first contains the same elements as second
        self.assertCountEqual(wkt, wkt_geometry_collection)


if __name__ == "__main__":
    unittest.main()
