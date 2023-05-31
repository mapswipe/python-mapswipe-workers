import json
import os
import urllib.request
from dataclasses import dataclass
from typing import Dict, List

from osgeo import ogr

from mapswipe_workers.definitions import DATA_PATH, CustomError, logger
from mapswipe_workers.firebase.firebase import Firebase
from mapswipe_workers.project_types.arbitrary_geometry import grouping_functions as g
from mapswipe_workers.project_types.base.project import BaseGroup, BaseProject
from mapswipe_workers.project_types.base.tile_server import BaseTileServer
from mapswipe_workers.utils.api_calls import geojsonToFeatureCollection, ohsome


@dataclass
class ArbitraryGeometryGroup(BaseGroup):
    pass


# Since Arbitrary Geometry Tasks do not have a ProjectId and GroupId
# they do not inherit from BaseTask
@dataclass
class ArbitraryGeometryTask:
    taskId: str
    geojson: dict
    properties: dict
    geometry: str


class ArbitraryGeometryProject(BaseProject):
    def __init__(self, project_draft: dict) -> None:
        super().__init__(project_draft)
        self.groups: Dict[str, ArbitraryGeometryGroup] = {}
        self.tasks: Dict[
            str, List[ArbitraryGeometryTask]
        ] = {}  # dict keys are group ids

        # set group size
        self.groupSize = project_draft["groupSize"]
        self.geometry = project_draft["geometry"]
        self.inputType = project_draft["inputType"]
        self.tileServer = vars(BaseTileServer(project_draft["tileServer"]))
        if "filter" in project_draft.keys():
            self.filter = project_draft["filter"]
        if "TMId" in project_draft.keys():
            self.TMId = project_draft["TMId"]

    def handle_input_type(self, raw_input_file: str):
        """
        Handle different input types.

        Input (inputGeometries) can be:
        'aoi_file' -> query ohsome with aoi from geometry then write
            result to raw_input_file
        a Link (str) -> download geojson from link and write to raw_input_file
        a TMId -> get project info from geometry and query ohsome
            for objects, then write to raw_input_file.
        """
        if not isinstance(self.geometry, str):
            self.geometry = geojsonToFeatureCollection(self.geometry)
            self.geometry = json.dumps(self.geometry)

        if self.inputType == "aoi_file":
            logger.info("aoi file detected")
            # write string to geom file
            ohsome_request = {"endpoint": "elements/geometry", "filter": self.filter}

            result = ohsome(ohsome_request, self.geometry, properties="tags, metadata")
            with open(raw_input_file, "w") as geom_file:
                json.dump(result, geom_file)
        elif self.inputType == "TMId":
            logger.info("TMId detected")
            hot_tm_project_id = int(self.TMId)
            ohsome_request = {"endpoint": "elements/geometry", "filter": self.filter}
            result = ohsome(ohsome_request, self.geometry, properties="tags, metadata")
            result["properties"] = {}
            result["properties"]["hot_tm_project_id"] = hot_tm_project_id
            with open(raw_input_file, "w") as geom_file:
                json.dump(result, geom_file)
        elif self.inputType == "link":
            logger.info("link detected")
            urllib.request.urlretrieve(self.geometry, raw_input_file)

    def validate_geometries(self):
        raw_input_file = (
            f"{DATA_PATH}/" f"input_geometries/raw_input_{self.projectId}.geojson"
        )
        valid_input_file = (
            f"{DATA_PATH}/" f"input_geometries/valid_input_{self.projectId}.geojson"
        )

        if not os.path.isdir("{}/input_geometries".format(DATA_PATH)):
            os.mkdir("{}/input_geometries".format(DATA_PATH))

        # input can be file, HOT TM projectId or link to geojson, after the call,
        # whatever the input is will be made
        # to a geojson file containing buildings in an area in raw_input_file
        self.handle_input_type(raw_input_file)

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
        feature_count = layer.GetFeatureCount()
        if feature_count < 1:
            err = "empty file. No geometries provided"
            # TODO: How to user logger and exceptions?
            logger.warning(f"{self.projectId} - check_input_geometry - {err}")
            raise CustomError(err)
        elif feature_count > 100000:
            err = f"Too many Geometries: {feature_count}"
            logger.warning(f"{self.projectId} - check_input_geometry - {err}")
            raise CustomError(err)

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
            fid = feature.GetFID()

            if not feat_geom.IsValid():
                layer.DeleteFeature(fid)
                logger.warning(
                    f"{self.projectId}"
                    f" - check_input_geometries - "
                    f"deleted invalid feature {fid}"
                )

            # we accept only POLYGON or MULTIPOLYGON geometries
            elif geom_name not in ["POLYGON", "MULTIPOLYGON"]:
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
        self.raw_groups = g.group_input_geometries(
            self.validInputGeometries, self.groupSize
        )

        for group_id, item in self.raw_groups.items():
            self.groups[group_id] = ArbitraryGeometryGroup(
                projectId=self.projectId,
                groupId=group_id,
                numberOfTasks=0,
                progress=0,
                finishedCount=0,
                requiredCount=0,
            )
        logger.info(
            f"{self.projectId} " f"- create_groups - " f"created groups dictionary"
        )

    def create_tasks(self):
        for group_id, item in self.raw_groups.items():
            features = item["features"]
            f_ids = item["feature_ids"]
            task_list = []
            for i, f_id in enumerate(f_ids):
                feature = features[i]
                task = ArbitraryGeometryTask(
                    taskId=f"t{f_id}",
                    geojson=feature["geometry"],
                    geometry=ogr.CreateGeometryFromJson(
                        str(feature["geometry"])
                    ).ExportToWkt(),
                    properties=feature["properties"],
                )
                task_list.append(task)
            if task_list:
                self.tasks[group_id] = task_list
            else:
                # remove group if it would contain no tasks
                self.groups.pop(group_id)
                logger.info(
                    f"group in project {self.projectId} is not valid: {group_id}"
                )
        # remove raw groups after task creation
        del self.raw_groups

    def save_tasks_to_firebase(self, projectId: str, tasks: dict):
        firebase = Firebase()
        firebase.save_tasks_to_firebase(projectId, tasks, useCompression=True)
