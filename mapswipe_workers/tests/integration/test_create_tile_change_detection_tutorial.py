import unittest

from click.testing import CliRunner

from mapswipe_workers import auth, mapswipe_workers
from tests.integration import tear_down


class TestCreateTileChangeDetectionTutorial(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        tear_down.delete_test_data(self.project_id)

    def test_create_tile_classification_tutorial(self):
        runner = CliRunner()
        runner.invoke(mapswipe_workers.run_create_tutorials, catch_exceptions=False)

        fb_db = auth.firebaseDB()
        ref = fb_db.reference(f"/v2/projects/{self.project_id}")
        result = ref.get(shallow=True)
        self.assertIsNotNone(result)

        ref = fb_db.reference(f"/v2/groups/{self.project_id}")
        result = ref.get(shallow=True)
        self.assertIsNotNone(result)

        ref = fb_db.reference(f"/v2/tasks/{self.project_id}")
        result = ref.get(shallow=True)
        self.assertIsNotNone(result)


if __name__ == "__main__":
    unittest.main()
