import unittest

import set_up
import tear_down
from mapswipe_workers import auth
from mapswipe_workers.firebase_to_postgres import archive_project


class TestArchiveProject(unittest.TestCase):
    def setUp(self):
        self.project_id = set_up.create_test_project("build_area")

    def tearDown(self):
        tear_down.delete_test_project(self.project_id)

    def test_firebase_changes(self):
        """Test if groups, tasks and results are deleted from Firebase."""
        archive_project.archive_project([self.project_id])

        fb_db = auth.firebaseDB()
        ref = fb_db.reference("v2/groups/{0}".format(self.project_id))
        self.assertIsNone(ref.get())

        ref = fb_db.reference("v2/tasks/{0}".format(self.project_id))
        self.assertIsNone(ref.get())

        ref = fb_db.reference("v2/results/{0}".format(self.project_id))
        self.assertIsNone(ref.get())

    def test_postgres_changes(self):
        """Test if postgres project is archived."""
        archive_project.archive_project([self.project_id])

        pg_db = auth.postgresDB()
        sql_query = "SELECT status FROM projects WHERE project_id = {}".format(
            self.project_id
        )
        result = pg_db.retr_query(sql_query)
        self.assertEqual(result, "archived")

    def test_project_id_equals_none(self):
        """Test for project id equals None."""
        archive_project.archive_project([None])

        fb_db = auth.firebaseDB()
        ref = fb_db.reference("v2/groups/")
        self.assertIsNotNone(ref.get())

        ref = fb_db.reference("v2/tasks/")
        self.assertIsNotNone(ref.get())

        ref = fb_db.reference("v2/results/")
        self.assertIsNotNone(ref.get())

    def test_project_id_equals_empty_str(self):
        """Test for poject id equals empty string."""
        archive_project.archive_project([""])

        fb_db = auth.firebaseDB()
        ref = fb_db.reference("v2/groups/")
        self.assertIsNotNone(ref.get())

        ref = fb_db.reference("v2/tasks/")
        self.assertIsNotNone(ref.get())

        ref = fb_db.reference("v2/results/")
        self.assertIsNotNone(ref.get())

    def test_project_id_not_exists(self):
        """Test for project id which does not exists."""
        archive_project.archive_project(["tuna"])

        fb_db = auth.firebaseDB()
        ref = fb_db.reference("v2/groups/")
        self.assertIsNotNone(ref.get())

        ref = fb_db.reference("v2/tasks/")
        self.assertIsNotNone(ref.get())

        ref = fb_db.reference("v2/results/")
        self.assertIsNotNone(ref.get())


if __name__ == "__main__":
    unittest.main()
