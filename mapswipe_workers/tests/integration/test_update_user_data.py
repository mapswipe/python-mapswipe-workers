import time
import unittest

import set_up
import tear_down

from mapswipe_workers import auth
from mapswipe_workers.firebase_to_postgres import update_data


class TestArchiveProject(unittest.TestCase):
    def setUp(self):
        self.user_id = set_up.create_test_user("tile_map_service_grid")
        self.user_ids = [self.user_id]

    def tearDown(self):
        tear_down.delete_test_user(self.user_ids)

    def test_no_users_in_postgres(self):
        """Test update users when no users are in postgres yet."""
        update_data.update_user_data()
        time.sleep(2)
        pg_db = auth.postgresDB()
        sql_query = "SELECT * FROM users WHERE user_id = '{0}'".format(self.user_id)
        result = pg_db.retr_query(sql_query)
        self.assertIsNotNone(result)

    def test_last_updated_users(self):
        """Test update users when some users are in postgres."""
        update_data.update_user_data()
        time.sleep(2)
        user_id = set_up.create_test_user("tile_map_service_grid", "test_user_2")
        self.user_ids.append(user_id)
        update_data.update_user_data()

        pg_db = auth.postgresDB()
        sql_query = "SELECT * FROM users WHERE user_id = '{0}'".format(user_id)
        result = pg_db.retr_query(sql_query)
        self.assertIsNotNone(result)

    def test_with_user_ids(self):
        update_data.update_user_data([self.user_id])
        time.sleep(2)
        pg_db = auth.postgresDB()
        sql_query = "SELECT * FROM users WHERE user_id = '{0}'".format(self.user_id)
        result = pg_db.retr_query(sql_query)
        self.assertIsNotNone(result)


if __name__ == "__main__":
    unittest.main()
