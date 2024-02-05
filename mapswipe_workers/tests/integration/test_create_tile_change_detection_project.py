import os
import unittest

from click.testing import CliRunner

from mapswipe_workers import auth, mapswipe_workers
from mapswipe_workers.utils.create_directories import create_directories
from tests import fixtures
from tests.fixtures import FIXTURE_DIR
from tests.integration import tear_down


class TestCreateTileClassificationProject(unittest.TestCase):
    def setUp(self):
        file_path = os.path.join(FIXTURE_DIR, "projectDrafts", "change_detection.json")
        self.project_id = fixtures.create_test_draft(
            file_path, "change_detection", "change_detection", draftType="projectDrafts"
        )
        create_directories()

    def tearDown(self):
        tear_down.delete_test_data(self.project_id)

    def test_create_tile_classification_project(self):
        runner = CliRunner()
        runner.invoke(mapswipe_workers.run_create_projects, catch_exceptions=False)

        pg_db = auth.postgresDB()
        query = "SELECT project_id FROM projects WHERE project_id = %s"
        result = pg_db.retr_query(query, [self.project_id])[0][0]
        self.assertEqual(result, self.project_id)

        query = "SELECT count(*)  FROM groups WHERE project_id = %s"
        result = pg_db.retr_query(query, [self.project_id])[0][0]
        self.assertEqual(result, 16)

        query = "SELECT count(*)  FROM tasks WHERE project_id = %s"
        result = pg_db.retr_query(query, [self.project_id])[0][0]
        self.assertEqual(result, 660)

        fb_db = auth.firebaseDB()
        ref = fb_db.reference(f"/v2/projects/{self.project_id}")
        result = ref.get(shallow=True)
        self.assertIsNotNone(result)

        ref = fb_db.reference(f"/v2/groups/{self.project_id}")
        result = ref.get(shallow=True)
        self.assertEqual(len(result), 16)

        ref = fb_db.reference(f"/v2/tasks/{self.project_id}")
        result = ref.get()
        self.assertEqual(sum([len(v) for k, v in result.items()]), 660)


if __name__ == "__main__":
    unittest.main()
