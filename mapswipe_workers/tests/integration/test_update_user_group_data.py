import copy
import unittest
from typing import Union
from unittest import mock

from base import BaseTestCase

from mapswipe_workers.firebase_to_postgres import update_data


class TestUpdateProjectData(BaseTestCase):
    class FbDbMock:
        url: Union[str, None]

        USER_GROUP_MOCK_DATA = {
            "user-group-1": {
                "name": "User Group 1",
                "description": "User Group 1 description",
                "users": {
                    "user-1": True,
                    "user-2": True,
                    "user-3": True,
                },
            },
            "user-group-2": {
                "name": "User Group 2",
                "description": "User Group 2 description",
                "users": {
                    "user-1": True,
                    "user-2": True,
                    "user-4": True,
                },
            },
            "user-group-3": {
                "name": "User Group 3",
                "description": "User Group 3 description",
                "users": {
                    "user-2": True,
                },
            },
            "user-group-4": {
                "name": "User Group 4",
                "description": "User Group 4 description",
                "users": {
                    "user-1": True,
                    "user-2": False,
                },
            },
            "user-group-5": {
                "name": "User Group 5",
                "description": "User Group 5 description",
            },
        }

        def __init__(self):
            # If we need to mutate data
            self.mock_data = copy.deepcopy(self.USER_GROUP_MOCK_DATA)

        def reference(self, url):
            # To track url. Used in get()
            self.url = url
            return self

        def get(self):
            if self.url is None:
                raise Exception("reference(url) should be called first. Please check.")
            if self.url.startswith("v2/userGroups/"):
                user_group_id = self.url.split("/")[-1]
                return self.mock_data.get(user_group_id)
            return {}

    @mock.patch("mapswipe_workers.firebase_to_postgres.update_data.auth.firebaseDB")
    def test_with_user_group_ids(self, fb_db_patch):
        """Test add/update user groups with no usergroups in postgres yet."""

        # Mock firebase db. Responses are simple here.
        fb_db_mock = self.FbDbMock()
        fb_db_patch.return_value = fb_db_mock

        update_data.update_user_group_full_data(
            [
                "user-group-1",
                "user-group-2",
                "user-group-3",
                "user-group-6",
            ]
        )

        # Define SQL Queries
        UG_QUERY = """
            SELECT
                user_group_id, name, description
            FROM user_groups
            ORDER BY user_group_id
            """
        T_UG_QUERY = """
            SELECT
                user_group_id, name, description
            FROM user_groups_temp
            ORDER BY user_group_id
            """
        UGM_QUERY = """
            SELECT
                user_group_id, user_id
            FROM user_groups_user_memberships
            ORDER BY user_group_id, user_id
            """
        T_UGM_QUERY = """
            SELECT
                user_group_id, user_id
            FROM user_groups_user_memberships_temp
            ORDER BY user_group_id, user_id
            """
        U_QUERY = "SELECT user_id FROM users ORDER BY user_id"

        for query, expected_value in [
            (
                UG_QUERY,
                [
                    ("user-group-1", "User Group 1", "User Group 1 description"),
                    ("user-group-2", "User Group 2", "User Group 2 description"),
                    ("user-group-3", "User Group 3", "User Group 3 description"),
                ],
            ),
            (T_UG_QUERY, []),
            (
                UGM_QUERY,
                [
                    ("user-group-1", "user-1"),
                    ("user-group-1", "user-2"),
                    ("user-group-1", "user-3"),
                    ("user-group-2", "user-1"),
                    ("user-group-2", "user-2"),
                    ("user-group-2", "user-4"),
                    ("user-group-3", "user-2"),
                ],
            ),
            (T_UGM_QUERY, []),
            (
                U_QUERY,
                [
                    ("user-1",),
                    ("user-2",),
                    ("user-3",),
                    ("user-4",),
                ],
            ),
        ]:
            self.assertEqual(
                expected_value,
                self.db.retr_query(query),
                (query, expected_value),
            )

        # Let's modify data for user-group-2
        fb_db_mock.mock_data["user-group-2"] = dict(
            name="User Group 2 (UPDATED)",
            description="User Group 2 descriptioni (UPDATED)",
            users={
                "user-1": True,
                "user-7": False,
                "user-8": True,
            },
        )
        # Trigger sync
        update_data.update_user_group_full_data(
            [
                "user-group-1",
                "user-group-2",
                "user-group-4",
                "user-group-5",
                "user-group-9",
            ]
        )

        for query, expected_value in [
            (
                UG_QUERY,
                [
                    ("user-group-1", "User Group 1", "User Group 1 description"),
                    (
                        "user-group-2",
                        "User Group 2 (UPDATED)",
                        "User Group 2 descriptioni (UPDATED)",
                    ),
                    ("user-group-3", "User Group 3", "User Group 3 description"),
                    ("user-group-4", "User Group 4", "User Group 4 description"),
                    ("user-group-5", "User Group 5", "User Group 5 description"),
                ],
            ),
            (T_UG_QUERY, []),
            (
                UGM_QUERY,
                [
                    ("user-group-1", "user-1"),
                    ("user-group-1", "user-2"),
                    ("user-group-1", "user-3"),
                    ("user-group-2", "user-1"),
                    ("user-group-2", "user-2"),
                    ("user-group-2", "user-4"),
                    ("user-group-2", "user-8"),
                    ("user-group-3", "user-2"),
                    ("user-group-4", "user-1"),
                ],
            ),
            (T_UGM_QUERY, []),
            (
                U_QUERY,
                [
                    ("user-1",),
                    ("user-2",),
                    ("user-3",),
                    ("user-4",),
                    ("user-8",),
                ],
            ),
        ]:
            self.assertEqual(
                expected_value,
                self.db.retr_query(query),
                (query, expected_value),
            )


if __name__ == "__main__":
    unittest.main()
