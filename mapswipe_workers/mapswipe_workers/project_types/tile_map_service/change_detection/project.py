from mapswipe_workers.firebase.firebase import Firebase
from mapswipe_workers.project_types.base.tile_server import BaseTileServer
from mapswipe_workers.project_types.tile_map_service.project import (
    TileClassificationProject,
)


class ChangeDetectionProject(TileClassificationProject):
    def __init__(self, project_draft: dict):
        super().__init__(project_draft)
        self.tileServerB = vars(BaseTileServer(project_draft["tileServerB"]))

    def save_tasks_to_firebase(self, projectId: str, tasks: list):
        firebase = Firebase()
        firebase.save_tasks_to_firebase(projectId, tasks)
