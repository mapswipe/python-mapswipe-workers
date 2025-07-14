from dataclasses import dataclass

from mapswipe_workers.definitions import logger
from mapswipe_workers.firebase.firebase import Firebase
from mapswipe_workers.project_types.tutorial import BaseTutorial
from mapswipe_workers.project_types.validate_image.project import (
    ValidateImageGroup,
    ValidateImageTask,
)


@dataclass
class ValidateImageTutorialTask(ValidateImageTask):
    # TODO(tnagorra): Check if we need projectId and groupId in tutorial task
    projectId: str
    groupId: str
    referenceAnswer: int
    screen: int


class ValidateImageTutorial(BaseTutorial):

    def __init__(self, tutorial_draft):
        # this will create the basis attributes
        super().__init__(tutorial_draft)

        self.groups = dict()
        self.tasks = dict()
        self.images = tutorial_draft["images"]

    def create_tutorial_groups(self):
        """Create group for the tutorial based on provided examples in images."""

        # NOTE: The groupId must be a numeric 101. It's hardcoded in save_tutorial_to_firebase
        group = ValidateImageGroup(
            groupId=101,
            projectId=self.projectId,
            numberOfTasks=len(self.images),
            progress=0,
            finishedCount=0,
            requiredCount=0,
        )
        self.groups[101] = group

        logger.info(
            f"{self.projectId} - create_tutorial_groups - created groups dictionary"
        )

    def create_tutorial_tasks(self):
        """Create the tasks dict based on provided examples in geojson file."""
        task_list = []
        for image_metadata in self.images:
            image_metadata = ValidateImageTutorialTask(
                projectId=self.projectId,
                groupId=101,
                taskId=image_metadata["sourceIdentifier"],
                fileName=image_metadata["fileName"],
                url=image_metadata["url"],
                geometry="",
                referenceAnswer=image_metadata["referenceAnswer"],
                screen=image_metadata["screen"],
            )
            task_list.append(image_metadata)

        if task_list:
            self.tasks[101] = task_list
        else:
            logger.info(f"group in project {self.projectId} is not valid.")

        logger.info(
            f"{self.projectId} - create_tutorial_tasks - created tasks dictionary"
        )

    def save_tutorial(self):
        firebase = Firebase()
        firebase.save_tutorial_to_firebase(
            self, self.groups, self.tasks, useCompression=False
        )
        logger.info(self.tutorialDraftId)
        firebase.drop_tutorial_draft(self.tutorialDraftId)
