from urllib.request import urlretrieve

from mapswipe_workers.firebase.firebase import Firebase
from mapswipe_workers.firebase_to_postgres.transfer_results import (
    save_results_to_postgres,
    truncate_temp_results,
)
from mapswipe_workers.project_types.arbitrary_geometry.project import (
    ArbitraryGeometryProject,
)


class DigitizationProject(ArbitraryGeometryProject):
    def __init__(self, project_draft):
        super().__init__(project_draft)
        self.drawType = project_draft["drawType"]

        # web app uses optional maxZoom to restrict the interactive web map zoom
        if "maxZoom" in project_draft["tileServer"].keys():
            self.tileServer["maxZoom"] = project_draft["tileServer"]["maxZoom"]

    def handle_input_type(self, raw_input_file: str):
        """
        Input (self.geometry) can be:
        a Link (str) -> download geojson from link and write to raw_input_file
        """
        urlretrieve(self.geometry, raw_input_file)

    def save_tasks_to_firebase(self, projectId: str, tasks: dict):
        firebase = Firebase()
        firebase.save_tasks_to_firebase(projectId, tasks, useCompression=False)

    @staticmethod
    def save_results_to_postgres(results_file, project_id, filter_mode):
        truncate_temp_results(temp_table="results_geometry_temp")
        save_results_to_postgres(
            results_file,
            project_id,
            filter_mode,
            result_temp_table="results_geometry_temp",
            result_table="mapping_sessions_results_geometry",
        )
