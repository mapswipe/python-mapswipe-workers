import unittest

from . import set_up
from . import tear_down
from click.testing import CliRunner

from mapswipe_workers import auth, mapswipe_workers
from mapswipe_workers.utils.create_directories import create_directories


class TestCreateTileClassificationTutorial(unittest.TestCase):
    def setUp(self):
        self.project_id = set_up.create_test_tutorial_draft(
            "tile_classification", "tile_classification"
        )
        create_directories()

    def tearDown(self):
        tear_down.delete_test_data(self.project_id)

    def test_create_tile_classification_tutorial(self):
        runner = CliRunner()
        runner.invoke(mapswipe_workers.run_create_tutorials)

        fb_db = auth.firebaseDB()
        ref = fb_db.reference(f"/v2/projects/{self.project_id}")
        result = ref.get(shallow=True)
        self.assertIsNotNone(result)

        ref = fb_db.reference(f"/v2/groups/{self.project_id}")
        result = ref.get(shallow=True)
        self.assertIsNotNone(result)

        # Tile classification projects do not have tasks in Firebase, but tutorials do
        ref = fb_db.reference(f"/v2/tasks/{self.project_id}")
        result = ref.get(shallow=True)
        self.assertIsNotNone(result)


if __name__ == "__main__":
    unittest.main()
