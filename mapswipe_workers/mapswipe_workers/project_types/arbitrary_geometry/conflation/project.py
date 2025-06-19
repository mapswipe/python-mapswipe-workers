import urllib

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


class ConflationProject(ArbitraryGeometryProject):
    def __init__(self, project_draft):
        super().__init__(project_draft)

    def handle_input_type(self, raw_input_file: str):
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
