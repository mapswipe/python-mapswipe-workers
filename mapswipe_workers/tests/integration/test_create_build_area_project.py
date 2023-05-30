import unittest

from click.testing import CliRunner

from mapswipe_workers import auth, mapswipe_workers
from mapswipe_workers.utils.create_directories import create_directories

from . import set_up, tear_down


class TestCreateProject(unittest.TestCase):
    def setUp(self):
        self.project_id = set_up.create_test_project_draft(
            "tile_map_service_grid", "build_area"
        )
        create_directories()

    def tearDown(self):
        tear_down.delete_test_data(self.project_id)

    def test_create_build_area_project(self):
        runner = CliRunner()
        runner.invoke(mapswipe_workers.run_create_projects)

        pg_db = auth.postgresDB()
        query = "SELECT project_id FROM projects WHERE project_id = %s"
        result = pg_db.retr_query(query, [self.project_id])[0][0]
        self.assertEqual(result, self.project_id)

        fb_db = auth.firebaseDB()
        ref = fb_db.reference(f"/v2/projects/{self.project_id}")
        result = ref.get(shallow=True)
        self.assertIsNotNone(result)

        ref = fb_db.reference(f"/v2/groups/{self.project_id}")
        result = ref.get(shallow=True)
        self.assertIsNotNone(result)

        # Build area project do not have tasks in Firebase
        ref = fb_db.reference(f"/v2/tasks/{self.project_id}")
        result = ref.get(shallow=True)
        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
