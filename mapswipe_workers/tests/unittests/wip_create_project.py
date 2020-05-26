import unittest
from tests.unittests import set_up
from tests.unittests import tear_down
from click.testing import CliRunner
from mapswipe_workers import auth, mapswipe_workers


class TestCreateProject(unittest.TestCase):
    def setUp(self):
        self.project_id = set_up.create_test_project_draft("build_area")

    def tearDown(self):
        tear_down.delete_test_data(self.project_id)

    def test_create_project(self):
        runner = CliRunner()
        runner.invoke(mapswipe_workers.run_create_projects)

        pg_db = auth.postgresDB()
        query = "SELECT * FROM projects WHERE project_id = '{0}'".format(
            self.project_id
        )
        result = pg_db.retr_query(query)
        self.assertIsNone(result)

        fb_db = auth.firebaseDB()
        ref = fb_db.reference("/v2/projects/{0}".format(self.project_id))
        result = ref.get()
        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
