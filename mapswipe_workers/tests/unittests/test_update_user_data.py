import unittest

from mapswipe_workers import auth
from mapswipe_workers.firebase_to_postgres import update_data

import set_up
import tear_down


class TestArchiveProject(unittest.TestCase):
    def setUp(self):
        self.user_id = set_up.create_test_user("build_area")

    def tearDown(self):
        tear_down.delete_test_data(self.user_id)

    def test_no_users_in_postgres(self):
        """Test update users when no users are in postgres yet."""
        update_data.update_user_data()
        pg_db = auth.postgresDB()
        sql_query = "SELECT * FROM users WHERE user_id = '{0}'".format(self.user_id)
        result = pg_db.retr_query(sql_query)
        self.assertIsNotNone(result)

    def test_last_updated_users(self):
        """Test update users when some users are in postgres."""
        update_data.update_user_data()
        user_id = set_up.create_test_user("build_area", user_id="test_user")
        update_data.update_user_data()

        pg_db = auth.postgresDB()
        sql_query = "SELECT * FROM users WHERE user_id = '{0}'".format(user_id)
        result = pg_db.retr_query(sql_query)
        self.assertIsNotNone(result)

    def test_with_user_ids(self):
        update_data.update_user_data([self.user_id])
        pg_db = auth.postgresDB()
        sql_query = "SELECT * FROM users WHERE user_id = '{0}'".format(self.user_id)
        result = pg_db.retr_query(sql_query)
        self.assertIsNotNone(result)


if __name__ == "__main__":
    unittest.main()
