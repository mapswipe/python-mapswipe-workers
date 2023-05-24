import io
import math
from zipfile import ZipFile, is_zipfile

# TODO import MediaClassificationGroup
import requests
from google.cloud import storage

from mapswipe_workers.config import FIREBASE_STORAGE_BUCKET
from mapswipe_workers.firebase.firebase import Firebase
from mapswipe_workers.project_types.base.project import BaseProject
from mapswipe_workers.project_types.media_classification.group import Group


class MediaClassificationProject(BaseProject):
    def __init__(self, project_draft: dict):
        super().__init__(project_draft)
        self.mediaCredits = project_draft.get("mediaCredits", None)
        self.medialist = []
        self.mediaurl = project_draft["mediaurl"]
        self.answerLabels = project_draft.get("answerLabels", None)
        self.get_media()

    def get_media(self):
        blob_path = "projectTypeMedia/" + self.projectId

        client = storage.Client()
        storage_bucket = client.get_bucket(FIREBASE_STORAGE_BUCKET)
        file = requests.get(self.mediaurl).content
        blob = storage_bucket.blob(blob_path + ".zip")
        blob.upload_from_string(file, content_type="application/zip", checksum="crc32c")

        zipbytes = io.BytesIO(blob.download_as_bytes())
        blob.delete()

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
        numberOfGroups = math.ceil(len(self.medialist) / self.groupSize)
        self.numberOfGroups = numberOfGroups
        for group_id in range(numberOfGroups):
            group = Group(self, group_id)
            group.create_tasks(self.medialist)
            self.groups.append(group)

    def save_to_firebase(self, project, groups, groupsOfTasks):
        self.save_project_to_firebase(project)
        self.save_groups_to_firebase(project["projectId"], groups)
        self.save_tasks_to_firebase(project["projectId"], groupsOfTasks)

    def save_project_to_firebase(self, project):
        firebase = Firebase()
        firebase.save_project_to_firebase(project)

    def save_groups_to_firebase(self, projectId: str, groups: list):
        firebase = Firebase()
        firebase.save_groups_to_firebase(projectId, groups)

    def save_tasks_to_firebase(self, projectId: str, tasks: list):
        firebase = Firebase()
        firebase.save_tasks_to_firebase(projectId, tasks, useCompression=False)

    def validate_geometries(self):
        # TODO check if media files are in the correct format
        pass

    def save_to_files(self, project):
        """We do not have any geometry so we pass here"""
        pass
