from abc import ABCMeta, abstractmethod
from mapswipe_workers import auth
from mapswipe_workers.definitions import logger, CustomError


class BaseTutorial(metaclass=ABCMeta):
    """The base class for creating."""

    def __init__(self, tutorial_draft):
        """The function to initialize a new tutorial."""
        self.lookFor = tutorial_draft["lookFor"]
        self.name = tutorial_draft["name"]
        self.projectId = tutorial_draft["projectId"]
        self.projectDetails = tutorial_draft["projectDetails"]
        self.progress = 0
        self.contributorCount = 0

    def save_tutorial(self):
        """Save the tutorial in Firebase."""

        tutorial = vars(self)
        groups = self.groups
        tasks = self.tasks

        tutorial.pop("groups", None)
        tutorial.pop("tasks", None)
        tutorial.pop("raw_tasks", None)
        tutorial.pop("examplesFile", None)

        fb_db = auth.firebaseDB()
        ref = fb_db.reference("")

        if not self.projectId or self.projectId == "":
            raise CustomError(
                f"""Given argument resulted in invalid Firebase Realtime Database reference.
                    Project Id is invalid: {self.projectId}"""
            )

        ref.update(
            {
                f"v2/projects/{self.projectId}": tutorial,
                f"v2/groups/{self.projectId}": groups,
                f"v2/tasks/{self.projectId}": tasks,
            }
        )

        logger.info(f"uploaded tutorial data to firebase for {self.projectId}")

    @abstractmethod
    def create_tutorial_groups():
        pass
