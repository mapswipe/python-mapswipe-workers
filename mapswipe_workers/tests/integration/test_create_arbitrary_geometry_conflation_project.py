import unittest

from click.testing import CliRunner

from mapswipe_workers import auth, mapswipe_workers
from mapswipe_workers.utils.create_directories import create_directories
from tests.integration import set_up, tear_down


class TestCreateConflationProject(unittest.TestCase):
    def setUp(self):
        self.project_id = set_up.create_test_project_draft("conflation", "conflation")

        create_directories()

    def tearDown(self):
        tear_down.delete_test_data(self.project_id)

    def test_create_footprint_project(self):
        runner = CliRunner()
        result = runner.invoke(
            mapswipe_workers.run_create_projects, catch_exceptions=False
        )
        if result.exit_code != 0:
            raise result.exception
        pg_db = auth.postgresDB()

        query = """
                    SELECT project_id, project_type_specifics
                    FROM projects
                    WHERE project_id = %s
                """
        result = pg_db.retr_query(query, [self.project_id])[0]
        self.assertEqual(result[0], self.project_id)

        fb_db = auth.firebaseDB()
        ref = fb_db.reference(f"/v2/projects/{self.project_id}")
        result = ref.get(shallow=True)
        self.assertIsNotNone(result)

        ref = fb_db.reference(f"/v2/groups/{self.project_id}")
        result = ref.get(shallow=True)
        self.assertIsNotNone(result)

        # Footprint projects have tasks in Firebase
        ref = fb_db.reference(f"/v2/tasks/{self.project_id}")
        result = ref.get(shallow=True)
        self.assertIsNotNone(result)


if __name__ == "__main__":
    unittest.main()
