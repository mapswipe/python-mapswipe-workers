from mapswipe_workers.project_types.tile_map_service.project import (
    TileMapServiceBaseProject,
)


class ClassificationProject(TileMapServiceBaseProject):
    def save_tasks_to_firebase(self, projectId: str, tasks: dict):
        # Tasks are not saved to firebase for this project type.
        # Clients can derive tasks themselves from group information.
        pass
