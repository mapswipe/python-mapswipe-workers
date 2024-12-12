from dataclasses import asdict, dataclass

from mapswipe_workers.definitions import logger
from mapswipe_workers.firebase.firebase import Firebase
from mapswipe_workers.project_types.street.project import StreetGroup, StreetTask
from mapswipe_workers.project_types.tutorial import BaseTutorial


@dataclass
class StreetTutorialTask(StreetTask):
    projectId: int
    taskId: str
    groupId: int
    referenceAnswer: int
    screen: int


class StreetTutorial(BaseTutorial):
    """The subclass for an arbitrary geometry based Tutorial."""

    def __init__(self, tutorial_draft):
        # this will create the basis attributes
        super().__init__(tutorial_draft)

        # self.projectId = tutorial_draft["projectId"]
        self.projectType = tutorial_draft["projectType"]
        self.tutorial_tasks = tutorial_draft["tasks"]
        self.groups = dict()
        self.tasks = dict()

    def create_tutorial_groups(self):
        """Create group for the tutorial based on provided examples in geojson file."""
        # load examples/tasks from file

        group = StreetGroup(
            groupId=101,
            projectId=self.projectId,
            numberOfTasks=len(self.tutorial_tasks),
            progress=0,
            finishedCount=0,
            requiredCount=0,
        )
        self.groups[101] = group

        # Add number of tasks for the group here. This needs to be set according to
        # the number of features/examples in the geojson file

        logger.info(
            f"{self.projectId}"
            f" - create_tutorial_groups - "
            f"created groups dictionary"
        )

    def create_tutorial_tasks(self):
        """Create the tasks dict based on provided examples in geojson file."""
        task_list = []
        for i, task in enumerate(self.tutorial_tasks):
            task = StreetTutorialTask(
                projectId=self.projectId,
                groupId=101,
                taskId=f"{task['taskImageId']}",
                geometry="",
                referenceAnswer=task["referenceAnswer"],
                screen=i,
            )
            task_list.append(asdict(task))
        if task_list:
            self.tasks[101] = task_list
        else:
            logger.info(f"group in project {self.projectId} is not valid.")

        logger.info(
            f"{self.projectId}"
            f" - create_tutorial_tasks - "
            f"created tasks dictionary"
        )

    def save_tutorial(self):
        firebase = Firebase()
        firebase.save_tutorial_to_firebase(
            self, self.groups, self.tasks, useCompression=True
        )
        logger.info(self.tutorialDraftId)
        firebase.drop_tutorial_draft(self.tutorialDraftId)
