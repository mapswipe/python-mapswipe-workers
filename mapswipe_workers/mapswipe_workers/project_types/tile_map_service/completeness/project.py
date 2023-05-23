from mapswipe_workers.project_types.base.tile_server import BaseTileServer
from mapswipe_workers.project_types.tile_map_service.project import (
    TileClassificationProject,
)


class CompletenessProject(TileClassificationBaseProject):
    def __init__(self, project_draft: dict):
        super().__init__(project_draft)
        self.tileServerB = vars(BaseTileServer(project_draft["tileServerB"]))

    def save_tasks_to_firebase(self, projectId: str, tasks: list):
        # Tasks are not saved to firebase for this project type.
        # Clients can derive tasks themselves from group information.
        pass
