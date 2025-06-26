from mapswipe_workers.definitions import logger
import math
from typing import Dict, List
from dataclasses import dataclass
from mapswipe_workers.firebase.firebase import Firebase
from mapswipe_workers.firebase_to_postgres.transfer_results import (
    results_to_file,
    save_results_to_postgres,
    truncate_temp_results,
)
from mapswipe_workers.project_types.project import BaseGroup, BaseProject
from mapswipe_workers.generate_stats.project_stats import (
    get_statistics_for_integer_result_project,
)


@dataclass
class ValidateImageGroup(BaseGroup):
    pass


@dataclass
class ValidateImageTask:
    # TODO(tnagorra): We need to check if fileName should be saved on project
    # NOTE: We do not need to add projectId and groupId so we are not extending BaseTask

    # NOTE: taskId is the sourceIdentifier
    taskId: str

    fileName: str
    url: str

    # NOTE: This is not required but required by the base class
    geometry: str


class ValidateImageProject(BaseProject):
    def __init__(self, project_draft):
        super().__init__(project_draft)
        self.groups: Dict[str, ValidateImageGroup] = {}
        self.tasks: Dict[str, List[ValidateImageTask]] = {}  # dict keys are group ids

        # NOTE: This is a standard structure defined on manager dashboard.
        # It's derived from other formats like COCO.
        # The transfromation is done in manager dashboard.
        self.images = project_draft["images"]

    def save_tasks_to_firebase(self, projectId: str, tasks: dict):
        firebase = Firebase()
        firebase.save_tasks_to_firebase(projectId, tasks, useCompression=False)

    @staticmethod
    def results_to_postgres(results: dict, project_id: str, filter_mode: bool):
        """How to move the result data from firebase to postgres."""
        results_file, user_group_results_file = results_to_file(results, project_id)
        truncate_temp_results()
        save_results_to_postgres(results_file, project_id, filter_mode)
        return user_group_results_file

    @staticmethod
    def get_per_project_statistics(project_id, project_info):
        """How to aggregate the project results."""
        return get_statistics_for_integer_result_project(
            project_id, project_info, generate_hot_tm_geometries=False
        )

    def validate_geometries(self):
        pass

    def save_to_files(self, project):
        """We do not have any geometry so we pass here"""
        pass

    def create_groups(self):
        self.numberOfGroups = math.ceil(len(self.images) / self.groupSize)
        for group_index in range(self.numberOfGroups):
            self.groups[f"g{group_index + 100}"] = ValidateImageGroup(
                projectId=self.projectId,
                groupId=f"g{group_index + 100}",
                progress=0,
                finishedCount=0,
                requiredCount=0,
                numberOfTasks=self.groupSize,
            )
        logger.info(f"{self.projectId} - create_groups - created groups dictionary")

    def create_tasks(self):
        if len(self.groups) == 0:
            raise ValueError("Groups needs to be created before tasks can be created.")
        for group_id, group in self.groups.items():
            self.tasks[group_id] = []
            for i in range(self.groupSize):
                # FIXME: We should try not to mutate values
                image_metadata = self.images.pop()
                task = ValidateImageTask(
                    taskId=image_metadata["sourceIdentifier"],
                    fileName=image_metadata["fileName"],
                    url=image_metadata["url"],
                    geometry="",
                )
                self.tasks[group_id].append(task)

                # list now empty? if usual group size is not reached
                # the actual number of tasks for the group is updated
                if not self.images:
                    group.numberOfTasks = i + 1
                    break
