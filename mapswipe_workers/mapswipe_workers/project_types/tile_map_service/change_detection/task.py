from mapswipe_workers.project_types.tile_map_service.task import TileClassificationTask
from mapswipe_workers.utils import tile_functions


class ChangedetectionTask(TileClassificationTask):
    def __init__(self, group: object, project: object, TileX: str, TileY: str):
        super().__init__(group, project, TileX, TileY)
        self.urlB = tile_functions.tile_coords_zoom_and_tileserver_to_url(
            TileX, TileY, project.zoomLevel, project.tileServerB
        )
