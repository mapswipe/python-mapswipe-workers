import unittest
import uuid

import set_up
import tear_down
from mapswipe_workers import auth
from mapswipe_workers.firebase_to_postgres import update_data


class TestUpdateUserData(unittest.TestCase):
    def setUp(self):
        self.user_ids = []
        self.num_users = 15
        for i in range(0, self.num_users):
            user_id = f"test_user_{uuid.uuid4()}"
            set_up.create_test_user(
                project_type="tile_map_service_grid", user_id=user_id
            )
            self.user_ids.append(user_id)

    def tearDown(self):
        tear_down.delete_test_user(self.user_ids)

    def test_no_users_in_postgres(self):
        """Test update users when no users are in postgres yet."""
        update_data.update_user_data()
        pg_db = auth.postgresDB()
        sql_query = "SELECT * FROM users WHERE user_id = ANY( %(user_ids)s )"
        result = pg_db.retr_query(sql_query, {"user_ids": self.user_ids})
        self.assertEqual(len(result), self.num_users)

    def test_last_updated_users(self):
        """Test update users when some users are in postgres."""
        update_data.update_user_data()
        user_id = set_up.create_test_user("tile_map_service_grid", "test_user_2")
        self.user_ids.append(user_id)
        update_data.update_user_data()

        pg_db = auth.postgresDB()
        sql_query = "SELECT * FROM users WHERE user_id = %(user_id)s"
        result = pg_db.retr_query(sql_query, {"user_id": user_id})
        self.assertIsNotNone(result)

    def test_with_user_ids(self):
        update_data.update_user_data(self.user_ids)
        pg_db = auth.postgresDB()
        sql_query = "SELECT * FROM users WHERE user_id = ANY ( %(user_ids)s )"
        result = pg_db.retr_query(sql_query, {"user_ids": self.user_ids})
        self.assertEqual(len(result), self.num_users)


if __name__ == "__main__":
    unittest.main()
