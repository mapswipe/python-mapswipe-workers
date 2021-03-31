import unittest

import set_up
import tear_down

from mapswipe_workers import auth
from mapswipe_workers.definitions import CustomError
from mapswipe_workers.firebase_to_postgres import delete_project


class TestDeleteProject(unittest.TestCase):
    def setUp(self):
        self.project_id = set_up.create_test_project(
            "tile_map_service_grid", "build_area", results=True
        )

    def tearDown(self):
        tear_down.delete_test_data(self.project_id)

    def test_deletion(self):
        """Test if tasks, groups, project and results are deleted."""
        delete_project.delete_project([self.project_id])

        fb_db = auth.firebaseDB()
        ref = fb_db.reference(f"v2/results/{self.project_id}")
        self.assertIsNone(ref.get())
        ref = fb_db.reference(f"v2/tasks/{self.project_id}")
        self.assertIsNone(ref.get())
        ref = fb_db.reference(f"v2/groups/{self.project_id}")
        self.assertIsNone(ref.get())
        ref = fb_db.reference(f"v2/groupsUsers/{self.project_id}")
        self.assertIsNone(ref.get())
        ref = fb_db.reference(f"v2/projects/{self.project_id}")
        self.assertIsNone(ref.get())

        pg_db = auth.postgresDB()
        sql_query = f"SELECT * FROM tasks WHERE project_id = '{self.project_id}'"
        result = pg_db.retr_query(sql_query)

        self.assertEqual(result, [])
        sql_query = f"SELECT * FROM groups WHERE project_id = '{self.project_id}'"
        result = pg_db.retr_query(sql_query)
        self.assertEqual(result, [])
        sql_query = f"SELECT * FROM projects WHERE project_id = '{self.project_id}'"
        result = pg_db.retr_query(sql_query)
        self.assertEqual(result, [])
        sql_query = "SELECT * FROM results WHERE project_id = '{}'".format(
            self.project_id
        )
        result = pg_db.retr_query(sql_query)
        self.assertEqual(result, [])

    def test_project_id_not_exists(self):
        """Test for project id which does not exists."""
        delete_project.delete_project(["tuna"])

        fb_db = auth.firebaseDB()
        ref = fb_db.reference("v2/results")
        self.assertIsNotNone(ref.get(shallow=True))
        ref = fb_db.reference("v2/tasks")
        self.assertIsNotNone(ref.get(shallow=True))
        ref = fb_db.reference("v2/groups")
        self.assertIsNotNone(ref.get(shallow=True))
        ref = fb_db.reference("v2/groupsUsers")
        self.assertIsNotNone(ref.get(shallow=True))
        ref = fb_db.reference("v2/projects")
        self.assertIsNotNone(ref.get(shallow=True))

        pg_db = auth.postgresDB()
        sql_query = f"SELECT * FROM tasks WHERE project_id = '{self.project_id}'"
        result = pg_db.retr_query(sql_query)
        self.assertNotEqual(result, [])
        sql_query = f"SELECT * FROM groups WHERE project_id = '{self.project_id}'"
        result = pg_db.retr_query(sql_query)
        self.assertNotEqual(result, [])
        sql_query = f"SELECT * FROM projects WHERE project_id = '{self.project_id}'"
        result = pg_db.retr_query(sql_query)
        self.assertNotEqual(result, [])
        sql_query = f"SELECT * FROM results WHERE project_id = '{self.project_id}'"
        result = pg_db.retr_query(sql_query)
        self.assertNotEqual(result, [])

    def test_project_id_equals_none(self):
        """Test for project id which does not exists."""
        delete_project.delete_project([None])

        fb_db = auth.firebaseDB()
        ref = fb_db.reference("v2/results")
        self.assertIsNotNone(ref.get(shallow=True))
        ref = fb_db.reference("v2/tasks")
        self.assertIsNotNone(ref.get(shallow=True))
        ref = fb_db.reference("v2/groups")
        self.assertIsNotNone(ref.get(shallow=True))
        ref = fb_db.reference("v2/groupsUsers")
        self.assertIsNotNone(ref.get(shallow=True))
        ref = fb_db.reference("v2/projects")
        self.assertIsNotNone(ref.get(shallow=True))

        pg_db = auth.postgresDB()
        sql_query = f"SELECT * FROM tasks WHERE project_id = '{self.project_id}'"
        result = pg_db.retr_query(sql_query)
        self.assertNotEqual(result, [])
        sql_query = f"SELECT * FROM groups WHERE project_id = '{self.project_id}'"
        result = pg_db.retr_query(sql_query)
        self.assertNotEqual(result, [])
        sql_query = f"SELECT * FROM projects WHERE project_id = '{self.project_id}'"
        result = pg_db.retr_query(sql_query)
        self.assertNotEqual(result, [])
        sql_query = f"SELECT * FROM results WHERE project_id = '{self.project_id}'"
        result = pg_db.retr_query(sql_query)
        self.assertNotEqual(result, [])

    def test_project_id_invalid(self):
        """Test for project id which does not exists."""
        self.assertRaises(CustomError, delete_project.delete_project, [{}])
        self.assertRaises(CustomError, delete_project.delete_project, [""])
        self.assertRaises(CustomError, delete_project.delete_project, ["/"])


if __name__ == "__main__":
    unittest.main()
