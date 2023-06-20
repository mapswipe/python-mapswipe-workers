from dataclasses import asdict, dataclass

from mapswipe_workers.firebase.firebase import Firebase
from mapswipe_workers.project_types.base.tile_server import BaseTileServer
from mapswipe_workers.project_types.tile_map_service.project import (
    TileMapServiceBaseProject,
    TileMapServiceBaseTask,
)
from mapswipe_workers.utils.tile_functions import tile_coords_zoom_and_tileserver_to_url


@dataclass
class ChangeDetectionTask(TileMapServiceBaseTask):
    urlB: str


class ChangeDetectionProject(TileMapServiceBaseProject):
    def __init__(self, project_draft: dict):
        super().__init__(project_draft)
        self.tileServerB = vars(BaseTileServer(project_draft["tileServerB"]))

    def create_tasks(self):
        super().create_tasks()
        # Add urlB attribute.
        for group_id, group in self.tasks.items():
            tasks = []
            for task in group:
                urlB = tile_coords_zoom_and_tileserver_to_url(
                    task.taskX,
                    task.taskY,
                    self.zoomLevel,
                    self.tileServerB,
                )
                # Cast super task class to completeness task class.
                tasks.append(ChangeDetectionTask(**asdict(task), urlB=urlB))
            self.tasks[group_id] = tasks

    def save_tasks_to_firebase(self, projectId: str, tasks: dict):
        """How to move the result data from firebase to postgres."""
        firebase = Firebase()
        firebase.save_tasks_to_firebase(projectId, tasks, useCompression=False)
