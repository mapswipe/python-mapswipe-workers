import time
import unittest

from mapswipe_workers import auth
from mapswipe_workers.config import FIREBASE_DB
from mapswipe_workers.definitions import CustomError
from mapswipe_workers.firebase_to_postgres import delete_project

from . import set_up, tear_down
from .base import BaseTestCase


class TestDeleteProject(BaseTestCase):
    def setUp(self):
        super().setUp()
        project_type = "tile_map_service_grid"
        fixture_name = "build_area"
        self.project_id = set_up.create_test_project(
            project_type, fixture_name, results=True
        )

    def tearDown(self):
        tear_down.delete_test_data(self.project_id)

    # This test is unreliable when running in Github Actions.
    # You should run this test locally.
    @unittest.skipIf(
        FIREBASE_DB == "ci-mapswipe",
        "Test is unreliable when running in Github Actions",
    )
    def verify_firebase_empty(self):
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

    def verify_firebase_not_empty(self):
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

    def verify_postgres_empty(self):
        pg_db = auth.postgresDB()
        sql_query = f"SELECT * FROM tasks WHERE project_id = '{self.project_id}'"
        result = pg_db.retr_query(sql_query)
        self.assertListEqual(result, [])
        sql_query = f"SELECT * FROM groups WHERE project_id = '{self.project_id}'"
        result = pg_db.retr_query(sql_query)
        self.assertListEqual(result, [])
        sql_query = f"SELECT * FROM projects WHERE project_id = '{self.project_id}'"
        result = pg_db.retr_query(sql_query)
        self.assertListEqual(result, [])
        sql_query = (
            f"SELECT * FROM mapping_sessions WHERE project_id = '{self.project_id}'"
        )
        result = pg_db.retr_query(sql_query)
        self.assertListEqual(result, [])
        sql_query = f"""
                SELECT msr.*
                FROM mapping_sessions_results msr
                JOIN mapping_sessions ms USING (mapping_session_id)
                WHERE ms.project_id = '{self.project_id}'
            """
        result = pg_db.retr_query(sql_query)
        self.assertListEqual(result, [])

    def verify_postgres_not_empty(self):
        pg_db = auth.postgresDB()
        sql_query = f"SELECT * FROM tasks WHERE project_id = '{self.project_id}'"
        result = pg_db.retr_query(sql_query)
        self.assertGreater(len(result), 0)
        sql_query = f"SELECT * FROM groups WHERE project_id = '{self.project_id}'"
        result = pg_db.retr_query(sql_query)
        self.assertGreater(len(result), 0)
        sql_query = f"SELECT * FROM projects WHERE project_id = '{self.project_id}'"
        result = pg_db.retr_query(sql_query)
        self.assertGreater(len(result), 0)
        sql_query = (
            f"SELECT * FROM mapping_sessions WHERE project_id = '{self.project_id}'"
        )
        result = pg_db.retr_query(sql_query)
        self.assertGreater(len(result), 0)
        sql_query = f"""
            SELECT msr.*
            FROM mapping_sessions_results msr
            JOIN mapping_sessions ms USING (mapping_session_id)
            WHERE ms.project_id = '{self.project_id}'
        """
        result = pg_db.retr_query(sql_query)
        self.assertGreater(len(result), 0)

    def test_deletion(self):
        """Test if tasks, groups, project and results are deleted."""
        delete_project.delete_project([self.project_id])
        time.sleep(1)  # Wait for Firebase Functions to complete

        self.verify_firebase_empty()
        self.verify_postgres_empty()

    def test_project_id_not_exists(self):
        """Test for project id which does not exists."""
        delete_project.delete_project(["tuna"])
        time.sleep(5)  # Wait for Firebase Functions to complete

        self.verify_firebase_not_empty()
        self.verify_postgres_not_empty()

    def test_project_id_empty(self):
        """Test deletion of empty project_id list."""
        delete_project.delete_project([])
        time.sleep(5)  # Wait for Firebase Functions to complete

        self.verify_firebase_not_empty()
        self.verify_postgres_not_empty()

    def test_project_id_equals_none(self):
        """Test for project id which does not exists."""
        delete_project.delete_project([None])
        time.sleep(5)  # Wait for Firebase Functions to complete

        self.verify_firebase_not_empty()
        self.verify_postgres_not_empty()

    def test_project_id_invalid(self):
        """Test for project id which does not exists."""
        self.assertRaises(CustomError, delete_project.delete_project, [{}])
        self.assertRaises(CustomError, delete_project.delete_project, [""])
        self.assertRaises(CustomError, delete_project.delete_project, ["/"])


if __name__ == "__main__":
    unittest.main()
