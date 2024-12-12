import math
from dataclasses import dataclass
from typing import Dict, List

from mapswipe_workers.definitions import logger
from mapswipe_workers.firebase.firebase import Firebase
from mapswipe_workers.firebase_to_postgres.transfer_results import (
    results_to_file,
    save_results_to_postgres,
    truncate_temp_results,
)
from mapswipe_workers.generate_stats.project_stats import (
    get_statistics_for_integer_result_project,
)
from mapswipe_workers.project_types.project import BaseGroup, BaseProject, BaseTask
from mapswipe_workers.utils.process_mapillary import get_image_metadata
from mapswipe_workers.utils.validate_input import (
    build_multipolygon_from_layer_geometries,
    check_if_layer_has_too_many_geometries,
    check_if_layer_is_empty,
    load_geojson_to_ogr,
    multipolygon_to_wkt,
    save_geojson_to_file,
)


@dataclass
class StreetGroup(BaseGroup):
    # todo: does client use this, or only for the implementation of project creation?
    pass


@dataclass
class StreetTask(BaseTask):
    geometry: str


class StreetProject(BaseProject):
    def __init__(self, project_draft):
        super().__init__(project_draft)
        self.groups: Dict[str, StreetGroup] = {}
        self.tasks: Dict[str, List[StreetTask]] = {}

        self.geometry = project_draft["geometry"]

        # TODO: validate inputs
        ImageMetadata = get_image_metadata(
            self.geometry,
            is_pano=project_draft.get("isPano", None),
            start_time=project_draft.get("startTimestamp", None),
            end_time=project_draft.get("endTimestamp", None),
            organization_id=project_draft.get("organizationId", None),
            sampling_threshold=project_draft.get("samplingThreshold", None),
        )

        self.imageIds = ImageMetadata["ids"]
        self.imageGeometries = ImageMetadata["geometries"]

    def save_tasks_to_firebase(self, projectId: str, tasks: dict):
        firebase = Firebase()
        firebase.save_tasks_to_firebase(projectId, tasks, useCompression=False)

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
        self.inputGeometriesFileName = save_geojson_to_file(
            self.projectId, self.geometry
        )
        layer, datasource = load_geojson_to_ogr(
            self.projectId, self.inputGeometriesFileName
        )

        # check if inputs fit constraints
        check_if_layer_is_empty(self.projectId, layer)

        multi_polygon, project_area = build_multipolygon_from_layer_geometries(
            self.projectId, layer
        )

        check_if_layer_has_too_many_geometries(self.projectId, multi_polygon)

        del datasource
        del layer

        logger.info(
            f"{self.projectId}" f" - validate geometry - " f"input geometry is correct."
        )
        wkt_geometry = multipolygon_to_wkt(multi_polygon)
        return wkt_geometry

    def create_groups(self):
        self.numberOfGroups = math.ceil(len(self.imageIds) / self.groupSize)
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
                    geometry=self.imageGeometries.pop(),
                    taskId=self.imageIds.pop(),
                )
                self.tasks[group_id].append(task)

                # list now empty? if usual group size is not reached
                # the actual number of tasks for the group is updated
                if not self.imageIds:
                    group.numberOfTasks = i + 1
                    break
