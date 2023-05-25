from dataclasses import asdict, dataclass

from mapswipe_workers.project_types.base.tile_server import BaseTileServer
from mapswipe_workers.project_types.tile_map_service.project import (
    TileMapServiceBaseProject,
    TileMapServiceBaseTask,
)
from mapswipe_workers.utils.tile_functions import tile_coords_zoom_and_tileserver_to_url


@dataclass
class CompletenessTask(TileMapServiceBaseTask):
    urlB: str


class CompletenessProject(TileMapServiceBaseProject):
    def __init__(self, project_draft: dict):
        super().__init__(project_draft)
        self.tileServerB = vars(BaseTileServer(project_draft["tileServerB"]))

    def save_tasks_to_firebase(self, projectId: str, tasks: list):
        # Tasks are not saved to firebase for this project type.
        # Clients can derive tasks themselves from group information.
        pass

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
                tasks.append(CompletenessTask(**asdict(task), urlB=urlB))
            self.tasks[group_id] = tasks
