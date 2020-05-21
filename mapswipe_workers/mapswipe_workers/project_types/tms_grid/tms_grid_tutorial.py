import json
from mapswipe_workers.definitions import logger
from mapswipe_workers.base.base_tutorial import BaseTutorial
from mapswipe_workers.base.base_tile_server import BaseTileServer
from mapswipe_workers.utils import tile_functions as t


class TMSGridTutorial(BaseTutorial):
    """The subclass for an TMS Grid based Tutorial."""

    def __init__(self, tutorial_draft):
        # this will create the basis attributes
        super().__init__(tutorial_draft)

        self.projectType = tutorial_draft["projectType"]
        self.zoomLevel = int(tutorial_draft.get("zoomLevel", 18))
        self.tileServer = vars(BaseTileServer(tutorial_draft["tileServer"]))
        self.examplesFile = tutorial_draft["examplesFile"]
        self.categories = tutorial_draft["categories"]
        self.groups = dict()
        self.tasks = dict()

        # get TileServerB for change detection and completeness type
        if self.projectType in [3, 4]:
            self.tileServerB = vars(BaseTileServer(tutorial_draft["tileServerB"]))

        # TODO: make sure that "tutorial" is fine from the app side
        #  currently it expects "completeness_tutorial" for instance
        status_dict = {
            1: "build_area_tutorial",
            3: "change_detection_tutorial",
            4: "completeness_tutorial",
        }
        self.status = status_dict[self.projectType]

    def create_tutorial_groups(self):

        # load examples/tasks from file
        with open(self.examplesFile, "r") as f:
            self.raw_tasks = json.load(f)[
                "features"
            ]  # get list of features from geojson file

        number_of_screens = len(self.categories)
        # create the groups dict to be uploaded in Firebase
        self.groups[101] = {
            "xMax": 100
            + (2 * number_of_screens)
            - 1,  # this depends on the number of screens/tasks to show
            "xMin": 100,  # this will be always set to 100
            "yMax": 131074,  # this is set to be at the equator
            "yMin": 131072,  # this is set to be at the equator
            "requiredCount": 5,  # this is not needed from back end perspective, maybe for client
            "finishedCount": 0,  # this is not needed from back end perspective, maybe for client
            "groupId": 101,  # a tutorial has only one group
            "projectId": self.projectId,
            "numberOfTasks": len(
                self.raw_tasks
            ),  # this depends on the number of screens/tasks to show
            "progress": 0,  # this is not needed from back end perspective, maybe for client
        }

        if self.projectType in [3]:
            # need to adjust xMax and yMax for Change Detection projects
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
        number_of_screens = len(self.categories)

        for screen in range(1, number_of_screens + 1):
            # get all tasks for this screen
            raw_tasks_screen = [
                d for d in self.raw_tasks if d["properties"]["screen"] in [screen]
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
                    "taskX": tile_x_tutorial,  # need to set this correctly based on screen
                    "taskY": tile_y_tutorial,  # need to set this correctly based on screen
                    "groupId": 101,  # a tutorial has only one group
                    "projectId": self.projectId,
                    "referenceAnswer": raw_task["properties"]["reference"],
                    "category": raw_task["properties"]["category"],
                    "url": t.tile_coords_zoom_and_tileserver_to_url(
                        tile_x, tile_y, self.zoomLevel, self.tileServer
                    ),
                }

                # Completeness and Change Detection projects use a second tile image url
                if self.projectType in [3, 4]:
                    task["urlB"] = t.tile_coords_zoom_and_tileserver_to_url(
                        tile_x, tile_y, self.zoomLevel, self.tileServerB
                    )

                self.tasks[101].append(task)

        logger.info(
            f"{self.projectId}"
            f" - create_tutorial_tasks - "
            f"created tasks dictionary"
        )
