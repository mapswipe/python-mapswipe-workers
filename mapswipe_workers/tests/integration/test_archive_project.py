import time
import unittest

from . import set_up
from . import tear_down

from mapswipe_workers import auth
from mapswipe_workers.config import FIREBASE_DB
from mapswipe_workers.firebase_to_postgres import archive_project


class TestArchiveProject(unittest.TestCase):
    def setUp(self):
        self.project_id = set_up.create_test_project(
            "tile_map_service_grid", "build_area", results=True
        )

    def tearDown(self):
        tear_down.delete_test_data(self.project_id)

    # This test is unreliable when running in Github Actions.
    # You should run this test locally.
    @unittest.skipIf(
        FIREBASE_DB == "ci-mapswipe",
        "Test is unreliable when running in Github Actions",
    )
    def test_changes(self):
        """Test if groups, tasks and results are deleted from Firebase."""
        archive_project.archive_project([self.project_id])

        time.sleep(1)  # Wait for Firebase Functions to complete

        fb_db = auth.firebaseDB()
        ref = fb_db.reference(f"v2/groups/{self.project_id}")
        self.assertIsNone(ref.get())

        ref = fb_db.reference(f"v2/groupsUsers/{self.project_id}")
        self.assertIsNone(ref.get())

        ref = fb_db.reference(f"v2/tasks/{self.project_id}")
        self.assertIsNone(ref.get())

        ref = fb_db.reference(f"v2/results/{self.project_id}")
        self.assertIsNone(ref.get())

        pg_db = auth.postgresDB()
        sql_query = "SELECT status FROM projects WHERE project_id = %s"
        result = pg_db.retr_query(sql_query, [self.project_id])[0][0]
        self.assertEqual(result, "archived")

    def test_project_id_not_exists(self):
        """Test for project id which does not exists."""
        archive_project.archive_project(["tuna"])

        time.sleep(1)  # Wait for Firebase Functions to complete

        fb_db = auth.firebaseDB()
        ref = fb_db.reference("v2/groups/")
        self.assertIsNotNone(ref.get(shallow=True))

        ref = fb_db.reference("v2/groupsUsers/")
        self.assertIsNotNone(ref.get(shallow=True))

        ref = fb_db.reference("v2/tasks/")
        self.assertIsNotNone(ref.get(shallow=True))

        ref = fb_db.reference("v2/results/")
        self.assertIsNotNone(ref.get(shallow=True))


if __name__ == "__main__":
    unittest.main()
