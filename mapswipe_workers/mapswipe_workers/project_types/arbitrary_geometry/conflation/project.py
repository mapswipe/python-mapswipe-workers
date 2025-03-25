import json
import urllib

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
from mapswipe_workers.project_types.arbitrary_geometry.project import (
    ArbitraryGeometryProject,
)
from mapswipe_workers.utils.api_calls import geojsonToFeatureCollection, ohsome


class ConflationProject(ArbitraryGeometryProject):
    def __init__(self, project_draft):
        super().__init__(project_draft)
        self.inputType = project_draft["inputType"]

    def handle_input_type(self, raw_input_file: str):
        """
        Handle different input types.

        Input (self.geometry) can be:
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

    def save_tasks_to_firebase(self, projectId: str, tasks: dict):
        firebase = Firebase()
        firebase.save_tasks_to_firebase(projectId, tasks, useCompression=True)

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
