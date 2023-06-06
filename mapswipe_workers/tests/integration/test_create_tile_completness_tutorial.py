import os
import unittest

from click.testing import CliRunner

from mapswipe_workers import auth, mapswipe_workers
from mapswipe_workers.utils.create_directories import create_directories
from tests import fixtures
from tests.fixtures import FIXTURE_DIR
from tests.integration import tear_down


class TestCreateCompletenessTutorial(unittest.TestCase):
    def setUp(self):
        file_path = os.path.join(FIXTURE_DIR, "tutorialDrafts", "completeness.json")
        self.project_id = fixtures.create_test_draft(
            file_path,
            "completeness",
            "completeness",
            draftType="tutorialDrafts",
        )
        create_directories()

    def tearDown(self):
        tear_down.delete_test_data(self.project_id)

    def test_create_completeness_tutorial(self):
        runner = CliRunner()
        runner.invoke(mapswipe_workers.run_create_tutorials, catch_exceptions=False)

        fb_db = auth.firebaseDB()
        ref = fb_db.reference(f"/v2/projects/tutorial_{self.project_id}")
        result = ref.get(shallow=True)
        self.assertIsNotNone(result)

        ref = fb_db.reference(f"/v2/groups/tutorial_{self.project_id}")
        result = ref.get(shallow=True)
        self.assertIsNotNone(result)

        # Tile classification projects do not have tasks in Firebase, but tutorials do
        ref = fb_db.reference(f"/v2/tasks/tutorial_{self.project_id}")
        result = ref.get(shallow=True)
        self.assertIsNotNone(result)


if __name__ == "__main__":
    unittest.main()
