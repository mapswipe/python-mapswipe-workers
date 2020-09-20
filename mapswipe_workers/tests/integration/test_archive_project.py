import time
import unittest

import set_up
import tear_down

from mapswipe_workers import auth
from mapswipe_workers.firebase_to_postgres import archive_project


class TestArchiveProject(unittest.TestCase):
    def setUp(self):
        self.project_id = set_up.create_test_project(
            "tile_map_service_grid", "build_area", results=True
        )
        time.sleep(4)  # Wait for Firebase Functions to complete

    def tearDown(self):
        tear_down.delete_test_data(self.project_id)

    def test_changes(self):
        """Test if groups, tasks and results are deleted from Firebase."""
        archive_project.archive_project([self.project_id])
        time.sleep(4)  # Wait for Firebase Functions to complete

        fb_db = auth.firebaseDB()
        ref = fb_db.reference("v2/groups/{0}".format(self.project_id))
        self.assertIsNone(ref.get())

        ref = fb_db.reference("v2/tasks/{0}".format(self.project_id))
        self.assertIsNone(ref.get())

        ref = fb_db.reference("v2/results/{0}".format(self.project_id))
        self.assertIsNone(ref.get())

        pg_db = auth.postgresDB()
        sql_query = "SELECT status FROM projects WHERE project_id = '{}'".format(
            self.project_id
        )
        result = pg_db.retr_query(sql_query)[0][0]
        self.assertEqual(result, "archived")

    def test_project_id_not_exists(self):
        """Test for project id which does not exists."""
        archive_project.archive_project(["tuna"])
        time.sleep(4)  # Wait for Firebase Functions to complete

        fb_db = auth.firebaseDB()
        ref = fb_db.reference("v2/groups/")
        self.assertIsNotNone(ref.get(shallow=True))

        ref = fb_db.reference("v2/tasks/")
        self.assertIsNotNone(ref.get(shallow=True))

        ref = fb_db.reference("v2/results/")
        self.assertIsNotNone(ref.get(shallow=True))


if __name__ == "__main__":
    unittest.main()
