from dataclasses import dataclass
from typing import Dict, List

from mapswipe_workers.definitions import logger
from mapswipe_workers.firebase.firebase import Firebase
from mapswipe_workers.project_types.tile_map_service.project import (
    TileMapServiceBaseGroup,
    TileMapServiceBaseTask,
)
from mapswipe_workers.project_types.tile_server import BaseTileServer
from mapswipe_workers.project_types.tutorial import BaseTutorial
from mapswipe_workers.utils import tile_functions as t


@dataclass
class TileMapServiceBaseTutorialTask(TileMapServiceBaseTask):
    taskId_real: str
    referenceAnswer: int
    screen: int


class TileMapServiceBaseTutorial(BaseTutorial):
    """The subclass for an TMS Grid based Tutorial."""

    def __init__(self, tutorial_draft):
        super().__init__(tutorial_draft)

        self.groups: Dict[str, TileMapServiceBaseGroup] = {}
        self.tasks: Dict[str, List[TileMapServiceBaseTutorialTask]] = (
            {}
        )  # dict keys are group ids

        self.zoomLevel = int(tutorial_draft.get("zoomLevel", 18))
        self.tileServer = vars(BaseTileServer(tutorial_draft["tileServer"]))
        self.tutorial_tasks = tutorial_draft["tutorialTasks"]

    def create_tutorial_groups(self):
        """Create group for the tutorial based on provided examples in geojson file."""
        # load examples/tasks from file

        number_of_screens = len(self.screens)
        self.groups[101] = TileMapServiceBaseGroup(
            **{
                "xMax": 100
                + (2 * number_of_screens)
                - 1,  # this depends on the number of screens/tasks to show
                "xMin": 100,  # this will be always set to 100
                "yMax": 131074,  # this is set to be at the equator
                "yMin": 131072,  # this is set to be at the equator
                "requiredCount": 5,  # not needed from backend perspective (client?)
                "finishedCount": 0,  # not needed from backend perspective (client?)
                "groupId": 101,  # a tutorial has only one group
                "projectId": self.projectId,
                "numberOfTasks": len(
                    self.tutorial_tasks
                ),  # this depends on the number of screens/tasks to show
                "progress": 0,  # not needed from backend perspective, maybe for client
            }
        )

        logger.info(
            f"{self.projectId}"
            f" - create_tutorial_groups - "
            f"created groups dictionary"
        )

    def create_tutorial_tasks(self):
        """Create the tasks dict based on provided examples in geojson file."""
        self.tasks[101] = list()
        number_of_screens = len(self.screens)

        for screen in range(1, number_of_screens + 1):
            # get all tasks for this screen

            raw_tasks_screen = [
                d
                for d in self.tutorial_tasks["features"]
                if d["properties"]["screen"] in [screen]
            ]

            # sort by tile_x and tile_y
            raw_tasks_screen_sorted = sorted(
                raw_tasks_screen,
                key=lambda k: (k["properties"]["tile_x"], k["properties"]["tile_y"]),
            )

            for i, raw_task in enumerate(raw_tasks_screen_sorted):
                tile_x = raw_task["properties"]["tile_x"]
                tile_y = raw_task["properties"]["tile_y"]

                if i < 3:  # get adjusted tile_x to fit in tutorial data schema
                    tile_x_tutorial = self.groups[101].xMin + (2 * (screen - 1))
                else:
                    tile_x_tutorial = self.groups[101].xMin + (2 * (screen - 1)) + 1

                if i in [0, 3]:  # get adjusted tile_y to fit in tutorial data schema
                    tile_y_tutorial = self.groups[101].yMin
                elif i in [1, 4]:
                    tile_y_tutorial = self.groups[101].yMin + 1
                elif i in [2, 5]:
                    tile_y_tutorial = int(self.groups[101].yMin) + 2

                task = TileMapServiceBaseTutorialTask(
                    **{
                        "taskId_real": f"{self.zoomLevel}-{tile_x}-{tile_y}",
                        "taskId": (
                            f"{self.zoomLevel}-"
                            + f"{tile_x_tutorial}-"
                            + f"{tile_y_tutorial}"
                        ),
                        # need to set correctly based on screen
                        "taskX": tile_x_tutorial,
                        "taskY": tile_y_tutorial,
                        "groupId": "101",  # a tutorial has only one group
                        "projectId": self.projectId,
                        "referenceAnswer": raw_task["properties"]["reference"],
                        "screen": raw_task["properties"]["screen"],
                        "url": t.tile_coords_zoom_and_tileserver_to_url(
                            tile_x, tile_y, self.zoomLevel, self.tileServer
                        ),
                        "geometry": "",  # TODO: does this work?
                    }
                )

                self.tasks[101].append(task)

        logger.info(
            f"{self.projectId}"
            f" - create_tutorial_tasks - "
            f"created tasks dictionary"
        )

    def save_tutorial(self):
        firebase = Firebase()
        firebase.save_tutorial_to_firebase(
            self, self.groups, self.tasks, useCompression=False
        )
        logger.info(self.tutorialDraftId)
        firebase.drop_tutorial_draft(self.tutorialDraftId)
