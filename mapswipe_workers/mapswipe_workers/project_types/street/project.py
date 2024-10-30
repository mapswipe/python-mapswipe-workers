import json
import os
import urllib
import math

from osgeo import ogr
from dataclasses import dataclass
from mapswipe_workers.definitions import DATA_PATH, logger
from mapswipe_workers.firebase.firebase import Firebase
from mapswipe_workers.firebase_to_postgres.transfer_results import (
    results_to_file,
    save_results_to_postgres,
    truncate_temp_results,
)
from mapswipe_workers.generate_stats.project_stats import (
    get_statistics_for_integer_result_project,
)
from mapswipe_workers.project_types.project import (
    BaseProject, BaseTask, BaseGroup
)
from mapswipe_workers.utils.process_mapillary import get_image_ids


@dataclass
class StreetGroup(BaseGroup):
    # todo: does client use this, or only for the implementation of project creation?
    pass


@dataclass
class StreetTask(BaseTask):
    pass

class StreetProject(BaseProject):
    def __init__(self, project_draft):
        super().__init__(project_draft)
        self.groups: Dict[str, StreetGroup] = {}
        self.tasks: Dict[str, List[StreetTask]] = (
            {}
        )

        self.geometry = project_draft["geometry"]
        self.imageList = get_image_ids()

    def save_tasks_to_firebase(self, projectId: str, tasks: dict):
        firebase = Firebase()
        firebase.save_tasks_to_firebase(projectId, tasks)

    @staticmethod
    def results_to_postgres(results: dict, project_id: str, filter_mode: bool):
        """How to move the result data from firebase to postgres."""
        results_file, user_group_results_file = results_to_file(results, project_id)
        truncate_temp_results()
        save_results_to_postgres(results_file, project_id, filter_mode)
        return user_group_results_file

    @staticmethod
    def get_per_project_statistics(project_id, project_info):
        """How to aggregate the project results."""
        return get_statistics_for_integer_result_project(
            project_id, project_info, generate_hot_tm_geometries=False
        )

    def validate_geometries(self):
        raw_input_file = (
            f"{DATA_PATH}/input_geometries/raw_input_{self.projectId}.geojson"
        )

        if not os.path.isdir(f"{DATA_PATH}/input_geometries"):
            os.mkdir(f"{DATA_PATH}/input_geometries")

        valid_input_file = (
            f"{DATA_PATH}/input_geometries/valid_input_{self.projectId}.geojson"
        )

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

        self.inputGeometriesFileName = valid_input_file

        logger.info(
            f"{self.projectId}"
            f" - check_input_geometry - "
            f"filtered correct input geometries and created file: "
            f"{valid_input_file}"
        )
        return wkt_geometry

    def create_groups(self):
        self.numberOfGroups = math.ceil(len(self.imageList) / self.groupSize)
        for group_id in range(self.numberOfGroups):
            self.groups[f"g{group_id}"] = StreetGroup(
                projectId=self.projectId,
                groupId=f"g{group_id}",
                progress=0,
                finishedCount=0,
                requiredCount=0,
                numberOfTasks=self.groupSize,
            )

    def create_tasks(self):
        if len(self.groups) == 0:
            raise ValueError("Groups needs to be created before tasks can be created.")
        for group_id, group in self.groups.items():
            self.tasks[group_id] = []
            for i in range(self.groupSize):
                task = StreetTask(
                    projectId=self.projectId,
                    groupId=group_id,
                    taskId=self.imageList.pop(),
                )
                self.tasks[group_id].append(task)

                # list now empty? if usual group size is not reached
                # the actual number of tasks for the group is updated
                if not self.imageList:
                    group.numberOfTasks = i + 1
                    break

