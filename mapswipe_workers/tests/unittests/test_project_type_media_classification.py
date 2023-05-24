import os
import unittest
from unittest.mock import patch

from google.cloud import storage

from mapswipe_workers.config import FIREBASE_STORAGE_BUCKET
from mapswipe_workers.project_types.media_classification.project import (
    MediaClassificationProject,
)
from tests import fixtures


class TestMediaClassification(unittest.TestCase):
    def setUp(self):
        project_draft = fixtures.get_fixture(
            os.path.join("projectDrafts", "media_classification.json")
        )
        project_draft["projectDraftId"] = "bar"
        self.project = MediaClassificationProject(project_draft)

    def tearDown(self) -> None:
        client = storage.Client()
        storage_bucket = client.get_bucket(FIREBASE_STORAGE_BUCKET)
        storage_bucket.delete_blobs(
            [
                url.replace(
                    f"https://storage.googleapis.com/{FIREBASE_STORAGE_BUCKET}/", ""
                )
                for url in self.project.medialist
            ]
        )
        client.close()

    def test_init(self):
        self.assertEqual(self.project.mediaCredits, "credits")
        self.assertEqual(self.project.mediaurl, "https://example.com")
        self.assertFalse(self.project.medialist)

    def test_get_media(self):
        with patch(
            "mapswipe_workers.project_types.media_classification.project.requests.get"
        ) as mock_get:
            with open(
                os.path.join(
                    os.path.dirname(os.path.abspath(__file__)),
                    "..",
                    "fixtures",
                    "media.zip",
                ),
                "rb",
            ) as file:
                mock_get.return_value.content = file.read()

            self.project.get_media()
            self.assertTrue(self.project.medialist)

    def test_create_group(self):
        with patch(
            "mapswipe_workers.project_types.media_classification.project.requests.get"
        ) as mock_get:
            with open(
                os.path.join(
                    os.path.dirname(os.path.abspath(__file__)),
                    "..",
                    "fixtures",
                    "media.zip",
                ),
                "rb",
            ) as file:
                mock_get.return_value.content = file.read()

            self.project.get_media()

        task_url = self.project.medialist[0]
        self.project.create_groups()

        self.assertTrue(self.project.groups)
        self.assertEqual(self.project.groups[0].numberOfTasks, 1)
        self.assertEqual(self.project.groups[0].tasks[0].media, task_url)


if __name__ == "__main__":
    unittest.main()
