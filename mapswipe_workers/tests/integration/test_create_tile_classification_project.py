import unittest

from click.testing import CliRunner

from mapswipe_workers import auth, mapswipe_workers
from mapswipe_workers.utils.create_directories import create_directories
from tests.integration import set_up, tear_down


class TestCreateTileClassificationProject(unittest.TestCase):
    def setUp(self):
        self.project_id = set_up.create_test_project_draft(
            "tile_classification", "tile_classification"
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

        query = """
            SELECT project_id
            FROM projects
            WHERE project_id = %s
                and project_type_specifics::jsonb ? 'answerLabels'
        """
        result = pg_db.retr_query(query, [self.project_id])[0][0]
        self.assertEqual(result, self.project_id)

        query = "SELECT count(*)  FROM groups WHERE project_id = %s"
        result = pg_db.retr_query(query, [self.project_id])[0][0]
        self.assertEqual(result, 20)

        query = "SELECT count(*)  FROM tasks WHERE project_id = %s"
        result = pg_db.retr_query(query, [self.project_id])[0][0]
        self.assertEqual(result, 5040)

        fb_db = auth.firebaseDB()
        ref = fb_db.reference(f"/v2/projects/{self.project_id}")
        result = ref.get(shallow=True)
        self.assertIsNotNone(result)

        ref = fb_db.reference(f"/v2/groups/{self.project_id}")
        result = ref.get(shallow=True)
        self.assertEqual(len(result), 20)

        # Tile classification projects do not have tasks in Firebase
        ref = fb_db.reference(f"/v2/tasks/{self.project_id}")
        result = ref.get(shallow=True)
        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
