from urllib.request import urlretrieve

from mapswipe_workers.firebase.firebase import Firebase
from mapswipe_workers.project_types.arbitrary_geometry.project import (
    ArbitraryGeometryProject,
)


class DigitizationProject(ArbitraryGeometryProject):
    def __init__(self, project_draft):
        super().__init__(project_draft)
        self.drawType = project_draft["drawType"]

    def handle_input_type(self, raw_input_file: str):
        """
        Input (self.geometry) can be:
        a Link (str) -> download geojson from link and write to raw_input_file
        """
        urlretrieve(self.geometry, raw_input_file)

    def save_tasks_to_firebase(self, projectId: str, tasks: dict):
        firebase = Firebase()
        firebase.save_tasks_to_firebase(projectId, tasks, useCompression=False)
