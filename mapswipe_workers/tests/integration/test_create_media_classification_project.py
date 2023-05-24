import os
import unittest
from unittest.mock import patch

from click.testing import CliRunner

from mapswipe_workers import auth, mapswipe_workers
from mapswipe_workers.utils.create_directories import create_directories
from tests import fixtures
from tests.fixtures import FIXTURE_DIR
from tests.integration import tear_down


class TestCreateMediaClassificationProject(unittest.TestCase):
    def setUp(self):
        file_path = os.path.join(
            FIXTURE_DIR, "projectDrafts", "media_classification.json"
        )
        self.project_id = fixtures.create_test_project_draft(
            file_path, "media_classification", "media_classification"
        )
        create_directories()

    def tearDown(self):
        tear_down.delete_test_data(self.project_id)

    def test_create_media_classification_project(self):
        runner = CliRunner()
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
                runner.invoke(
                    mapswipe_workers.run_create_projects, catch_exceptions=False
                )

        pg_db = auth.postgresDB()
        query = "SELECT project_id FROM projects WHERE project_id = %s"
        result = pg_db.retr_query(query, [self.project_id])[0][0]
        self.assertEqual(result, self.project_id)

        query = "SELECT count(*)  FROM groups WHERE project_id = %s"
        result = pg_db.retr_query(query, [self.project_id])[0][0]
        self.assertEqual(result, 1)

        query = "SELECT count(*)  FROM tasks WHERE project_id = %s"
        result = pg_db.retr_query(query, [self.project_id])[0][0]
        self.assertEqual(result, 1)

        fb_db = auth.firebaseDB()
        ref = fb_db.reference(f"/v2/projects/{self.project_id}")
        result = ref.get(shallow=True)
        self.assertIsNotNone(result)

        ref = fb_db.reference(f"/v2/groups/{self.project_id}")
        result = ref.get(shallow=True)
        self.assertEqual(len(result), 1)

        # Tile classification projects do not have tasks in Firebase
        ref = fb_db.reference(f"/v2/tasks/{self.project_id}")
        result = ref.get(shallow=True)
        self.assertIsNotNone(result)


if __name__ == "__main__":
    unittest.main()
