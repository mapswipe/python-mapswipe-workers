import unittest

from . import set_up
from . import tear_down
from click.testing import CliRunner

from mapswipe_workers import auth, mapswipe_workers
from mapswipe_workers.utils.create_directories import create_directories


class TestCreateTileClassificationProject(unittest.TestCase):
    def setUp(self):
        self.project_id = set_up.create_test_project_draft(
            "tile_classification", "tile_classification_with_additional_attributes"
        )
        create_directories()

    def tearDown(self):
        tear_down.delete_test_data(self.project_id)

    def test_create_tile_classification_project(self):
        runner = CliRunner()
        runner.invoke(mapswipe_workers.run_create_projects)

        pg_db = auth.postgresDB()
        query = "SELECT project_type_specifics -> 'language' FROM projects WHERE project_id = %s"
        result = pg_db.retr_query(query, [self.project_id])[0][0]
        self.assertEqual(result, "de-de")

        query = "SELECT project_type_specifics -> 'appId' FROM projects WHERE project_id = %s"
        result = pg_db.retr_query(query, [self.project_id])[0][0]
        self.assertEqual(result, 99)

        query = "SELECT project_type_specifics -> 'manualUrl' FROM projects WHERE project_id = %s"
        result = pg_db.retr_query(query, [self.project_id])[0][0]
        self.assertEqual(result, "https://www.mapswipe.org")

        fb_db = auth.firebaseDB()
        ref = fb_db.reference(f"/v2/projects/{self.project_id}/language")
        result = ref.get(shallow=True)
        self.assertEqual(result, "de-de")

        ref = fb_db.reference(f"/v2/projects/{self.project_id}/appId")
        result = ref.get(shallow=True)
        self.assertEqual(result, 99)

        ref = fb_db.reference(f"/v2/projects/{self.project_id}/manualUrl")
        result = ref.get(shallow=True)
        self.assertEqual(result, "https://www.mapswipe.org")

if __name__ == "__main__":
    unittest.main()
