import time
import unittest

from mapswipe_workers import auth
from mapswipe_workers.config import FIREBASE_DB
from mapswipe_workers.definitions import CustomError
from mapswipe_workers.firebase_to_postgres import delete_project
from tests.integration import base, set_up, tear_down


class TestDeleteProjectDigitization(base.BaseTestCase):
    def setUp(self):
        self.project_id = project_type = fixture_name = "digitization"

        set_up.create_test_project(
            project_type,
            fixture_name,
            results=True,
            mapping_sessions_results="mapping_sessions_results_geometry",
        )

    def tearDown(self):
        tear_down.delete_test_data(self.project_id)


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
            FROM mapping_sessions_results_geometry msr
            JOIN mapping_sessions ms USING (mapping_session_id)
            WHERE ms.project_id = '{self.project_id}'
        """
        result = pg_db.retr_query(sql_query)
        self.assertGreater(len(result), 0)

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
                FROM mapping_sessions_results_geometry msr
                JOIN mapping_sessions ms USING (mapping_session_id)
                WHERE ms.project_id = '{self.project_id}'
            """

        result = pg_db.retr_query(sql_query)
        self.assertListEqual(result, [])

    def test_deletion(self):
        """Test if tasks, groups, project and results are deleted."""
        self.verify_postgres_not_empty()
        delete_project.delete_project([self.project_id])
        time.sleep(1)  # Wait for Firebase Functions to complete

        self.verify_postgres_empty()


if __name__ == "__main__":
    unittest.main()
