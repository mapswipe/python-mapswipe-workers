import io
from zipfile import ZipFile, is_zipfile

# TODO import MediaClassificationGroup
import requests
from google.cloud import storage

from mapswipe_workers.config import FIREBASE_STORAGE_BUCKET
from mapswipe_workers.firebase.firebase import Firebase
from mapswipe_workers.project_types.base.project import BaseProject


class MediaClassificationProject(BaseProject):
    def __init__(self, project_draft: dict):
        super().__init__(project_draft)
        self.mediaCredits = project_draft.get("mediaCredits", None)
        self.medialist = []
        self.mediaurl = project_draft["mediaurl"]

    def get_media(self):
        blob_path = "projectTypeMedia/" + self.projectId

        client = storage.Client()
        storage_bucket = client.get_bucket(FIREBASE_STORAGE_BUCKET)
        file = requests.get(self.mediaurl).content
        blob = storage_bucket.blob(blob_path + ".zip")
        blob.upload_from_string(file, content_type="application/zip", checksum="crc32c")

        zipbytes = io.BytesIO(blob.download_as_string())
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
        # TODO: This project needs tasks to be saved
        pass

    """
    def create_groups(self):
        # first step get properties of each group from extent
        raw_groups = tile_grouping_functions.extent_to_groups(
            self.validInputGeometries, self.zoomLevel, self.groupSize
        )

        for group_id, slice in raw_groups.items():
            group = TileClassificationGroup(self, group_id, slice)
            group.create_tasks(self)

            # only append valid groups
            if group.is_valid():
                self.groups.append(group)
    """

    def validate_geometries(self):
        # TODO check if media files are in the correct format
        pass
