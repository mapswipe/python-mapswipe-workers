import json

from mapswipe_workers.definitions import DATA_PATH, logger
from mapswipe_workers.project_types.arbitrary_geometry import grouping_functions as g
from mapswipe_workers.project_types.arbitrary_geometry.group import Group
from mapswipe_workers.project_types.base.tile_server import BaseTileServer
from mapswipe_workers.project_types.base.tutorial import BaseTutorial


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
        self.tasks = []

        # save tasks as geojson
        self.inputGeometries = (
            f"{DATA_PATH}/input_geometries/valid_input_{self.projectId}.geojson"
        )

        with open(self.inputGeometries, "w") as f:
            json.dump(self.tutorial_tasks, f)

    def create_tutorial_groups(self):
        """Create group for the tutorial based on provided examples in geojson file."""
        # load examples/tasks from file

        # create the groups dict to be uploaded in Firebase
        self.groups = dict()

        group = Group(self, groupId=101)
        self.groups[101] = vars(group)

        # add number of tasks for the group here
        # this needs to be set according to the examples for the tutorial
        self.groups[101]["numberOfTasks"] = len(self.tutorial_tasks)

        logger.info(
            f"{self.projectId}"
            f" - create_tutorial_groups - "
            f"created groups dictionary"
        )

    def create_tutorial_tasks(self):
        """Create the tasks dict based on provided examples in geojson file."""

        raw_groups = g.group_input_geometries(
            self.inputGeometries, len(self.tutorial_tasks) + 1
        )
        for group_id, item in raw_groups.items():
            group = Group(self, groupId=101)
            group.create_tasks(
                item["feature_ids"],
                item["feature_geometries"],
                item["center_points"],
                item["reference"],
                item["screen"],
            )

        for task in group.tasks:
            logger.info(task)
            self.tasks.append(vars(task))

        logger.info(
            f"{self.projectId}"
            f" - create_tutorial_tasks - "
            f"created tasks dictionary"
        )
