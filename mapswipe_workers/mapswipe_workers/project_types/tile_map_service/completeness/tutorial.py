from mapswipe_workers.definitions import logger
from mapswipe_workers.project_types.base.tile_server import BaseTileServer
from mapswipe_workers.project_types.tile_map_service.tutorial import (
    TileMapServiceBaseTutorial,
)
from mapswipe_workers.utils import tile_functions


class CompletenessTutorial(TileMapServiceBaseTutorial):
    """The subclass for an TMS Grid based Tutorial."""

    def __init__(self, tutorial_draft):
        # this will create the basis attributes
        super().__init__(tutorial_draft)
        self.tileServerB = vars(BaseTileServer(tutorial_draft["tileServerB"]))

    def create_tutorial_groups(self):
        """Create group for the tutorial based on provided examples in geojson file."""

        super().create_tutorial_groups()

        # need to adjust xMax and yMax for Change Detection projects
        # since they use a different view with only one tile per screen
        number_of_screens = len(self.screens)
        self.groups[101]["xMax"] = str(100 + (number_of_screens - 1))
        self.groups[101]["yMax"] = str(self.groups[101]["yMin"])

        logger.info(
            f"{self.projectId}"
            f" - create_tutorial_groups - "
            f"adjusted groups dictionary for CompletenessTutorial"
        )

    def create_tutorial_tasks(self):
        """Create the tasks dict based on provided examples in geojson file."""

        super().create_tutorial_tasks()

        for task in self.tasks[101]:
            _, tile_x, tile_y = task["taskId_real"].split("-")
            task["urlB"] = tile_functions.tile_coords_zoom_and_tileserver_to_url(
                int(tile_x), int(tile_y), self.zoomLevel, self.tileServerB
            )

        logger.info(
            f"{self.projectId}"
            f" - create_tutorial_tasks - "
            f"adjusted tasks dictionary for CompletenessTutorial"
        )
