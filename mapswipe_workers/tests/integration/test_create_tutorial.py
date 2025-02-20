import unittest

from click.testing import CliRunner

from mapswipe_workers import auth, mapswipe_workers
from mapswipe_workers.utils.create_directories import create_directories
from tests.integration import set_up, tear_down


class TestCreateTileClassificationProject(unittest.TestCase):
    def setUp(self):
        self.tutorial_id = set_up.create_test_tutorial_draft(
            "street",
            "street",
            "test_tile_classification_tutorial",
        )

        self.project_id = set_up.create_test_project_draft(
            "street",
            "street",
            "test_tile_classification_tutorial",
            tutorial_id=self.tutorial_id,
        )
        create_directories()

    def tearDown(self):
        tear_down.delete_test_data(self.project_id, self.tutorial_id)

    def test_create_tile_classification_project(self):
        runner = CliRunner()
        runner.invoke(mapswipe_workers.run_create_tutorials, catch_exceptions=False)
        runner.invoke(mapswipe_workers.run_create_projects, catch_exceptions=False)

        fb_db = auth.firebaseDB()
        ref = fb_db.reference(f"/v2/projects/{self.project_id}")
        result = ref.get()
        self.assertEqual(result["tutorialId"], self.tutorial_id)

        ref = fb_db.reference(f"/v2/projects/{self.tutorial_id}")
        result = ref.get(shallow=True)
        self.assertIsNotNone(result)


if __name__ == "__main__":
    unittest.main()
