import unittest

from mapswipe_workers import auth
from mapswipe_workers.firebase_to_postgres import archive_project
import create_test_project


class TestArchiveProject(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Set up before tests are run."""
        cls.project_id = create_test_project(1)
        archive_project.archive_project(cls.project_id)

    @classmethod
    def tearDownClass(cls):
        """Tear down after tests are run."""
        pg_db = auth.postgresDB()
        sql_query = "DELETE FROM projects WHERE project_id = {0}".format(cls.project_id)
        pg_db.query(sql_query)

        fb_db = auth.firebaseDB()
        ref = fb_db.reference("v2/projects/{0}".format(cls.project_id))
        ref.set({})

        ref = fb_db.reference("v2/groups/{0}".format(cls.project_id))
        ref.set({})

        ref = fb_db.reference("v2/tasks/{0}".format(cls.project_id))
        ref.set({})

        ref = fb_db.reference("v2/results/{0}".format(cls.project_id))
        ref.set({})

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
        sql_query = "SELECT archived FROM projects WHERE project_id = {}".format(
            self.project_id
        )
        result = pg_db.retr_query(sql_query)
        self.assertEqual(result, "archived")


if __name__ == "__main__":
    unittest.main()
