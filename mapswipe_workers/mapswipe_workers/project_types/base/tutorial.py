from abc import ABC, abstractmethod

from mapswipe_workers import auth
from mapswipe_workers.definitions import CustomError, ProjectType, logger
from mapswipe_workers.project_types.base import BaseGroup, BaseTask
from mapswipe_workers.utils import gzip_str


class BaseTutorial(ABC):
    def __init__(self, tutorial_draft):
        # TODO: should be abstract attributes
        self.groups: dict[str, BaseGroup]
        self.tasks: dict[str, list[BaseTask]]  # dict keys are group ids

        # the id of the tutorial
        self.projectId = f"tutorial_{tutorial_draft['tutorialDraftId']}"
        self.lookFor = tutorial_draft["lookFor"]
        self.name = tutorial_draft["name"]
        self.tutorialDraftId = tutorial_draft["tutorialDraftId"]
        self.projectDetails = "This is a tutorial"
        self.progress = 0
        self.contributorCount = 0
        self.exampleImage1 = tutorial_draft.get("exampleImage1", None)
        self.exampleImage2 = tutorial_draft.get("exampleImage2", None)
        self.status = "tutorial"
        # need to filter out None values in list due to Firebase
        self.screens = list(filter(None, tutorial_draft["screens"]))

    def save_tutorial(self):
        """Save the tutorial in Firebase."""

        tutorial = vars(self)
        groups = self.groups
        tasks = self.tasks

        tutorial.pop("groups", None)
        tutorial.pop("tasks", None)
        tutorial.pop("raw_tasks", None)
        tutorial.pop("examplesFile", None)
        tutorial.pop("tutorial_tasks", None)

        fb_db = auth.firebaseDB()
        ref = fb_db.reference("")

        if not self.projectId or self.projectId == "":
            raise CustomError(
                "Given argument resulted in invalid "
                "Firebase Realtime Database reference. "
                f"Project Id is invalid: {self.projectId}"
            )

        if self.projectType in [ProjectType.FOOTPRINT.value]:
            # we compress tasks for footprint project type using gzip
            compressed_tasks = gzip_str.compress_tasks(tasks)
            tasks = {"101": compressed_tasks}

        ref.update(
            {
                f"v2/projects/{self.projectId}": tutorial,
                f"v2/groups/{self.projectId}": groups,
                f"v2/tasks/{self.projectId}": tasks,
            }
        )

        logger.info(f"uploaded tutorial data to firebase for {self.projectId}")

        ref = fb_db.reference(f"v2/tutorialDrafts/{self.tutorialDraftId}")
        ref.set({})

    @abstractmethod
    def create_tutorial_groups(self):
        pass

    @abstractmethod
    def create_tutorial_tasks(self):
        pass
