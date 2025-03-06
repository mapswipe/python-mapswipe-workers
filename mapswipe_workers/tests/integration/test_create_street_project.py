import unittest

from click.testing import CliRunner

from mapswipe_workers import auth, mapswipe_workers
from mapswipe_workers.definitions import logger
from mapswipe_workers.utils.create_directories import create_directories
from tests.integration import set_up, tear_down


class TestCreateStreetProject(unittest.TestCase):
    def setUp(self):
        self.project_id = [
            set_up.create_test_project_draft("street", "street"),
        ]
        create_directories()

    def tearDown(self):
        for element in self.project_id:
            tear_down.delete_test_data(element)

    def test_create_street_project(self):
        runner = CliRunner()
        result = runner.invoke(
            mapswipe_workers.run_create_projects, catch_exceptions=False
        )
        if result.exit_code != 0:
            raise result.exception
        pg_db = auth.postgresDB()
        for element in self.project_id:
            logger.info(f"Checking project {self.project_id}")
            query = "SELECT project_id FROM projects WHERE project_id = %s"
            result = pg_db.retr_query(query, [element])[0][0]
            self.assertEqual(result, element)

            # check if tasks made it to postgres
            query = """
                SELECT count(*)
                FROM tasks
                WHERE project_id = %s
            """
            result = pg_db.retr_query(query, [element])[0][0]
            self.assertGreater(result, 0)

            fb_db = auth.firebaseDB()
            ref = fb_db.reference(f"/v2/projects/{element}")
            result = ref.get(shallow=True)
            self.assertIsNotNone(result)

            ref = fb_db.reference(f"/v2/groups/{element}")
            result = ref.get(shallow=True)
            self.assertIsNotNone(result)

            # Street projects have tasks in Firebase
            ref = fb_db.reference(f"/v2/tasks/{element}")
            result = ref.get(shallow=True)
            self.assertIsNotNone(result)


if __name__ == "__main__":
    unittest.main()
