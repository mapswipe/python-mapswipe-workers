from abc import ABC, abstractmethod
from typing import Dict, List

from mapswipe_workers.project_types.project import BaseGroup, BaseTask


class BaseTutorial(ABC):
    def __init__(self, tutorial_draft):
        # TODO: should be abstract attributes
        self.groups: Dict[str, BaseGroup]
        self.tasks: Dict[str, List[BaseTask]]  # dict keys are group ids

        # the id of the tutorial
        self.projectId = f"tutorial_{tutorial_draft['tutorialDraftId']}"
        self.projectType = tutorial_draft["projectType"]
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

    @abstractmethod
    def save_tutorial(self):
        """Save the tutorial in Firebase."""

    @abstractmethod
    def create_tutorial_groups(self):
        pass

    @abstractmethod
    def create_tutorial_tasks(self):
        pass
