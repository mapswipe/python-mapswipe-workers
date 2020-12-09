import os
import urllib.request

from osgeo import ogr

from mapswipe_workers.definitions import DATA_PATH, CustomError, logger
from mapswipe_workers.project_types.arbitrary_geometry import grouping_functions as g
from mapswipe_workers.project_types.arbitrary_geometry.group import Group
from mapswipe_workers.project_types.base.project import BaseProject
from mapswipe_workers.project_types.base.tile_server import BaseTileServer


class Project(BaseProject):
    def __init__(self, project_draft: dict) -> None:
        super().__init__(project_draft)

        # set group size
        self.groupSize = project_draft["groupSize"]
        self.inputGeometries = project_draft["inputGeometries"]
        self.tileServer = vars(BaseTileServer(project_draft["tileServer"]))

    def validate_geometries(self):
        raw_input_file = (
            f"{DATA_PATH}/" f"input_geometries/raw_input_{self.projectId}.geojson"
        )
        valid_input_file = (
            f"{DATA_PATH}/" f"input_geometries/valid_input_{self.projectId}.geojson"
        )

        if not os.path.isdir("{}/input_geometries".format(DATA_PATH)):
            os.mkdir("{}/input_geometries".format(DATA_PATH))

        # download file from given url
        url = self.inputGeometries
        urllib.request.urlretrieve(url, raw_input_file)
        logger.info(
            f"{self.projectId}"
            f" - __init__ - "
            f"downloaded input geometries from url and saved as file: "
            f"{raw_input_file}"
        )
        self.inputGeometries = raw_input_file

        # open the raw input file and get layer
        driver = ogr.GetDriverByName("GeoJSON")
        datasource = driver.Open(raw_input_file, 0)
        try:
            layer = datasource.GetLayer()
            LayerDefn = layer.GetLayerDefn()
        except AttributeError:
            raise CustomError("Value error in input geometries file")

        # create layer for valid_input_file to store all valid geometries
        outDriver = ogr.GetDriverByName("GeoJSON")
        # Remove output geojson if it already exists
        if os.path.exists(valid_input_file):
            outDriver.DeleteDataSource(valid_input_file)
        outDataSource = outDriver.CreateDataSource(valid_input_file)
        outLayer = outDataSource.CreateLayer(
            "geometries", geom_type=ogr.wkbMultiPolygon
        )
        for i in range(0, LayerDefn.GetFieldCount()):
            fieldDefn = LayerDefn.GetFieldDefn(i)
            outLayer.CreateField(fieldDefn)
        outLayerDefn = outLayer.GetLayerDefn()

        # check if raw_input_file layer is empty
        if layer.GetFeatureCount() < 1:
            err = "empty file. No geometries provided"
            # TODO: How to user logger and exceptions?
            logger.warning(f"{self.projectId} - check_input_geometry - {err}")
            raise Exception(err)

        # get geometry as wkt
        # get the bounding box/ extent of the layer
        extent = layer.GetExtent()
        # Create a Polygon from the extent tuple
        ring = ogr.Geometry(ogr.wkbLinearRing)
        ring.AddPoint(extent[0], extent[2])
        ring.AddPoint(extent[1], extent[2])
        ring.AddPoint(extent[1], extent[3])
        ring.AddPoint(extent[0], extent[3])
        ring.AddPoint(extent[0], extent[2])
        poly = ogr.Geometry(ogr.wkbPolygon)
        poly.AddGeometry(ring)
        wkt_geometry = poly.ExportToWkt()

        # check if the input geometry is a valid polygon
        for feature in layer:
            feat_geom = feature.GetGeometryRef()
            geom_name = feat_geom.GetGeometryName()
            fid = feature.GetFID
            if not feat_geom.IsValid():
                layer.DeleteFeature(fid)
                logger.warning(
                    f"{self.projectId}"
                    f" - check_input_geometries - "
                    f"deleted invalid feature {fid}"
                )

            # we accept only POLYGON or MULTIPOLYGON geometries
            elif geom_name != "POLYGON" and geom_name != "MULTIPOLYGON":
                layer.DeleteFeature(fid)
                logger.warning(
                    f"{self.projectId}"
                    f" - check_input_geometries - "
                    f"deleted non polygon feature {fid}"
                )

            else:
                # Create output Feature
                outFeature = ogr.Feature(outLayerDefn)
                # Add field values from input Layer
                for i in range(0, outLayerDefn.GetFieldCount()):
                    outFeature.SetField(
                        outLayerDefn.GetFieldDefn(i).GetNameRef(), feature.GetField(i)
                    )
                outFeature.SetGeometry(feat_geom)
                outLayer.CreateFeature(outFeature)
                outFeature = None

        # check if layer is empty
        if layer.GetFeatureCount() < 1:
            err = "no geometries left after checking validity and geometry type."
            logger.warning(f"{self.projectId} - check_input_geometry - {err}")
            raise Exception(err)

        del datasource
        del outDataSource
        del layer

        self.validInputGeometries = valid_input_file

        logger.info(
            f"{self.projectId}"
            f" - check_input_geometry - "
            f"filtered correct input geometries and created file: "
            f"{valid_input_file}"
        )
        return wkt_geometry

    def create_groups(self):
        raw_groups = g.group_input_geometries(self.validInputGeometries, self.groupSize)

        for group_id, item in raw_groups.items():
            group = Group(self, group_id)
            group.create_tasks(
                item["feature_ids"],
                item["feature_geometries"],
                item["center_points"],
                item["reference"],
                item["screen"],
            )

            # only append valid groups
            if group.is_valid():
                self.groups.append(group)

        logger.info(
            f"{self.projectId} " f"- create_groups - " f"created groups dictionary"
        )
