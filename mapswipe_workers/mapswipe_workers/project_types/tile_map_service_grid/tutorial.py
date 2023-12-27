from mapswipe_workers.definitions import ProjectType, logger
from mapswipe_workers.project_types.base.tile_server import BaseTileServer
from mapswipe_workers.project_types.base.tutorial import BaseTutorial
from mapswipe_workers.utils import tile_functions as t


class Tutorial(BaseTutorial):
    """The subclass for an TMS Grid based Tutorial."""

    def __init__(self, tutorial_draft):
        # this will create the basis attributes
        super().__init__(tutorial_draft)

        self.projectType = tutorial_draft["projectType"]
        self.zoomLevel = int(tutorial_draft.get("zoomLevel", 18))
        self.tileServer = vars(BaseTileServer(tutorial_draft["tileServer"]))
        self.tutorial_tasks = tutorial_draft["tutorialTasks"]
        self.groups = dict()
        self.tasks = dict()

        # get TileServerB for Compare and completeness type
        if self.projectType in [3, 4]:
            self.tileServerB = vars(BaseTileServer(tutorial_draft["tileServerB"]))

    def create_tutorial_groups(self):
        """Create group for the tutorial based on provided examples in geojson file."""
        # load examples/tasks from file

        number_of_screens = len(self.screens)
        # create the groups dict to be uploaded in Firebase
        self.groups[101] = {
            "xMax": 100
            + (2 * number_of_screens)
            - 1,  # this depends on the number of screens/tasks to show
            "xMin": 100,  # this will be always set to 100
            "yMax": 131074,  # this is set to be at the equator
            "yMin": 131072,  # this is set to be at the equator
            "requiredCount": 5,  # not needed from backend perspective, maybe for client
            "finishedCount": 0,  # not needed from backend perspective, maybe for client
            "groupId": 101,  # a tutorial has only one group
            "projectId": self.projectId,
            "numberOfTasks": len(
                self.tutorial_tasks
            ),  # this depends on the number of screens/tasks to show
            "progress": 0,  # not needed from backend perspective, maybe for client
        }

        if self.projectType in [ProjectType.CHANGE_DETECTION.value]:
            # need to adjust xMax and yMax for Compare projects
            # since they use a different view with only one tile per screen
            self.groups[101]["xMax"] = str(100 + (number_of_screens - 1))
            self.groups[101]["yMax"] = str(self.groups[101]["yMin"])

        logger.info(
            f"{self.projectId}"
            f" - create_tutorial_groups - "
            f"created groups dictionary"
        )

    def create_tutorial_tasks(self):
        """Create the tasks dict based on provided examples in geojson file."""

        self.tasks = dict()
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
                    tile_x_tutorial = self.groups[101]["xMin"] + (2 * (screen - 1))
                else:
                    tile_x_tutorial = self.groups[101]["xMin"] + (2 * (screen - 1)) + 1

                if i in [0, 3]:  # get adjusted tile_y to fit in tutorial data schema
                    tile_y_tutorial = self.groups[101]["yMin"]
                elif i in [1, 4]:
                    tile_y_tutorial = self.groups[101]["yMin"] + 1
                elif i in [2, 5]:
                    tile_y_tutorial = int(self.groups[101]["yMin"]) + 2

                task = {
                    "taskId_real": f"{self.zoomLevel}-{tile_x}-{tile_y}",
                    "taskId": f"{self.zoomLevel}-{tile_x_tutorial}-{tile_y_tutorial}",
                    "taskX": tile_x_tutorial,  # need to set correctly based on screen
                    "taskY": tile_y_tutorial,  # need to set correctly based on screen
                    "groupId": 101,  # a tutorial has only one group
                    "projectId": self.projectId,
                    "referenceAnswer": raw_task["properties"]["reference"],
                    "screen": raw_task["properties"]["screen"],
                    "url": t.tile_coords_zoom_and_tileserver_to_url(
                        tile_x, tile_y, self.zoomLevel, self.tileServer
                    ),
                }

                # Completeness and Compare projects use a second tile image url
                if self.projectType in [
                    ProjectType.CHANGE_DETECTION.value,
                    ProjectType.COMPLETENESS.value,
                ]:
                    task["urlB"] = t.tile_coords_zoom_and_tileserver_to_url(
                        tile_x, tile_y, self.zoomLevel, self.tileServerB
                    )

                self.tasks[101].append(task)

        logger.info(
            f"{self.projectId}"
            f" - create_tutorial_tasks - "
            f"created tasks dictionary"
        )
