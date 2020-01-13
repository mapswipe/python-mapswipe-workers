import unittest

from mapswipe_workers import auth
from mapswipe_workers.firebase_to_postgres import archive_project

import set_up
import tear_down


class TestArchiveProject(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Set up before tests are run."""
        cls.project_id = set_up.create_test_data("project", "build_area")
        archive_project.archive_project(cls.project_id)

    @classmethod
    def tearDownClass(cls):
        """Tear down after tests are run."""
        tear_down.delete_test_data(cls.project_id)

    def test_firebase_changes(self):
        """Test if groups, tasks and results are deleted from Firebase."""
        fb_db = auth.firebaseDB()

        ref = fb_db.reference("v2/groups/{0}".format(self.project_id))
        self.assertFalse(ref.get())

        ref = fb_db.reference("v2/tasks/{0}".format(self.project_id))
        self.assertFalse(ref.get())

        ref = fb_db.reference("v2/results/{0}".format(self.project_id))
        self.assertFalse(ref.get())

    def test_postgres_changes(self):
        """Test if postgres project is archived."""
        pg_db = auth.postgresDB()
        # TODO archived is boolean or check status?
        sql_query = "SELECT archived FROM projects WHERE project_id = {}".format(
            self.project_id
        )
        result = pg_db.retr_query(sql_query)
        self.assertEqual(result, "archived")


if __name__ == "__main__":
    unittest.main()
