import io
import math
from dataclasses import dataclass
from typing import Dict, List
from zipfile import ZipFile, is_zipfile

import requests
from google.cloud import storage

from mapswipe_workers.config import FIREBASE_STORAGE_BUCKET
from mapswipe_workers.firebase.firebase import Firebase
from mapswipe_workers.firebase_to_postgres.transfer_results import (
    save_results_to_postgres,
    truncate_temp_results,
)
from mapswipe_workers.project_types.base.project import BaseGroup, BaseProject, BaseTask


@dataclass
class MediaClassificationGroup(BaseGroup):
    # todo: does client use this, or only for the implementation of project creation?
    numberOfTasks: int


@dataclass
class MediaClassificationTask(BaseTask):
    media: str
    geometry: str


class MediaClassificationProject(BaseProject):
    def __init__(self, project_draft: dict):
        super().__init__(project_draft)
        self.groups: Dict[str, MediaClassificationGroup] = {}
        self.tasks: Dict[
            str, List[MediaClassificationTask]
        ] = {}  # dict keys are group ids

        self.mediaCredits = project_draft.get("mediaCredits", None)
        self.medialist = []
        self.mediaurl = project_draft["mediaurl"]
        self.get_media()

        self.answerLabels = project_draft.get(
            "answerLabels",
            [
                {"color": "green", "label": "yes", "value": 1},
                {"color": "red", "label": "no", "value": 0},
                {"color": "grey", "label": "not sure", "value": 2},
            ],
        )

    def get_media(self):
        blob_path = "projectTypeMedia/" + self.projectId

        client = storage.Client()
        storage_bucket = client.get_bucket(FIREBASE_STORAGE_BUCKET)
        file = requests.get(self.mediaurl).content
        blob = storage_bucket.blob(blob_path + ".zip")
        blob.upload_from_string(file, content_type="application/zip", checksum="crc32c")

        zipbytes = io.BytesIO(blob.download_as_bytes())
        blob.delete()
        # TODO check if media files are in the correct format

        if is_zipfile(zipbytes):
            with ZipFile(zipbytes, "r") as myzip:
                for contentfilename in myzip.namelist():
                    contentfile = myzip.read(contentfilename)
                    blob = storage_bucket.blob(blob_path + "/" + contentfilename)
                    blob.upload_from_string(contentfile)

        for blob in storage_bucket.list_blobs(prefix=blob_path + "/"):
            blob.make_public()
            self.medialist.append(blob.public_url)
        client.close()

    def create_groups(self):
        self.numberOfGroups = math.ceil(len(self.medialist) / self.groupSize)
        for group_id in range(self.numberOfGroups):
            self.groups[f"g{group_id}"] = MediaClassificationGroup(
                projectId=self.projectId,
                groupId=f"g{group_id}",
                progress=0,
                finishedCount=0,
                requiredCount=0,
                numberOfTasks=self.groupSize,
            )

    def create_tasks(self):
        if len(self.groups) == 0:
            raise ValueError("Groups needs to be created before tasks can be created.")
        for group_id, group in self.groups.items():
            self.tasks[group_id] = []
            for i in range(self.groupSize):
                task = MediaClassificationTask(
                    projectId=self.projectId,
                    groupId=group_id,
                    taskId="t{}-{}".format(i, group.groupId),
                    geometry="",
                    media=self.medialist.pop(),
                )
                self.tasks[group_id].append(task)

                # list now empty? if usual group size is not reached
                # the actual number of tasks for the group is updated
                if not self.medialist:
                    group.numberOfTasks = i + 1
                    break

    def save_tasks_to_firebase(self, projectId: str, tasks: dict):
        firebase = Firebase()
        firebase.save_tasks_to_firebase(projectId, tasks, useCompression=False)

    def validate_geometries(self):
        pass

    def save_to_files(self, project):
        """We do not have any geometry so we pass here"""
        pass

    @staticmethod
    def save_results_to_postgres(results_file, project_id, filter_mode):
        truncate_temp_results()
        save_results_to_postgres(results_file, project_id, filter_mode)
