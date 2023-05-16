from mapswipe_workers.firebase.firebase import Firebase
from mapswipe_workers.project_types.base.project import BaseProject

from mapswipe_workers.project_types.base.tile_server import BaseTileServer

from mapswipe_workers.utils.validate_input import validate_geometries


class TileClassification(BaseProject):
    def __init__(self, project_draft: dict):
        super().__init__(project_draft)
        # Note: this will be overwritten by validate_geometry in mapswipe_workers.py
        self.geometry = project_draft["geometry"]
        self.zoomLevel = int(project_draft.get("zoomLevel", 18))
        self.tileServer = vars(BaseTileServer(project_draft["tileServer"]))

    def validate_geometries(self):
        wkt_geometry, self.validInputGeometries = validate_geometries(self.projectId, self.geometry, self.zoomLevel)
        return wkt_geometry

    def save_project_to_firebase(self, project):
        firebase = Firebase()
        firebase.save_project_to_firebase(project)

    def save_groups_to_firebase(self, projectId: str, groups: list):
        firebase = Firebase()
        firebase.save_groups_to_firebase(projectId, groups)

    def save_tasks_to_firebase(self, projectId: str, tasks: list):
        pass