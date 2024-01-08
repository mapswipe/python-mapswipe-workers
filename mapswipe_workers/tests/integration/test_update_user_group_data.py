import copy
import unittest
from typing import Union
from unittest import mock

from tests.integration import base
from mapswipe_workers.firebase_to_postgres import update_data


class TestUpdateProjectData(base.BaseTestCase):
    class FbDbMock:
        url: Union[str, None]

        USER_GROUP_MOCK_DATA = {
            "user-group-1": {
                "name": "User Group 1",
                "description": "User Group 1 description",
                "createdBy": "user-1",
                "createdAt": 1663039591857,
                "archivedBy": "user-2",
                "archivedAt": 1663039591887,
                "users": {
                    "user-1": True,
                    "user-2": True,
                    "user-3": True,
                },
                "userGroupMembershipLogs": {
                    "userId": "user-1",
                    "action": "join",
                    "timestamp": 1663039591857,
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
                "createdBy": "user-1",
                "createdAt": 1663039591857,
                "archivedBy": "user-2",
                "archivedAt": 1663039591887,
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

        USER_MOCK_DATA = {
            "user-1": {"username": "test user"},
            "user-2": {"username": "test user 2"},
        }
        MEMBERHSHIP_LOG_DATA = {
            "membership-1": {
                "userGroupId": "user-group-1",
                "userId": "user-1",
                "action": "join",
                "timestamp": 1663039597857,
            },
            "membership-2": {
                "userGroupId": "user-group-2",
                "userId": "user-2",
                "action": "leave",
                "timestamp": 1663039599857,
            },
        }

        def __init__(self):
            # If we need to mutate data
            self.mock_data = copy.deepcopy(self.USER_GROUP_MOCK_DATA)
            self.user_mock_data = copy.deepcopy(self.USER_MOCK_DATA)
            self.membership_mock_data = copy.deepcopy(self.MEMBERHSHIP_LOG_DATA)

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
            elif self.url.startswith("v2/users/"):
                user_id = self.url.split("/")[-1]
                return self.user_mock_data.get(user_id)
            elif self.url.startswith("v2/userGroupMembershipLogs/"):
                membership_id = self.url.split("/")[-1]
                return self.membership_mock_data.get(membership_id)
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

        # update user memeberhsip log data
        update_data.create_update_membership_data(
            [
                "membership-1",
                "membership-2",
            ]
        )

        # Define SQL Queries
        UG_QUERY = """
            SELECT
                user_group_id, name, description, is_archived
            FROM user_groups
            ORDER BY user_group_id
            """
        T_UG_QUERY = """
            SELECT
                user_group_id, name, description, is_archived
            FROM user_groups_temp
            ORDER BY user_group_id
            """
        UGM_QUERY = """
            SELECT
                user_group_id, user_id, is_active
            FROM user_groups_user_memberships
            ORDER BY user_group_id, user_id
            """
        T_UGM_QUERY = """
            SELECT
                user_group_id, user_id
            FROM user_groups_user_memberships_temp
            ORDER BY user_group_id, user_id
            """
        U_QUERY = "SELECT user_id FROM users WHERE user_id!='' \
        AND user_id IS NOT NULL ORDER BY user_id"

        UML_QUERY = (
            "SELECT user_group_id, user_id, action FROM user_groups_membership_logs"
        )

        for query, expected_value in [
            (
                    UG_QUERY,
                    [
                        ("user-group-1", "User Group 1", "User Group 1 description", True),
                        ("user-group-2", "User Group 2", "User Group 2 description", False),
                        ("user-group-3", "User Group 3", "User Group 3 description", True),
                    ],
            ),
            (T_UG_QUERY, []),
            (
                    UGM_QUERY,
                    [
                        ("user-group-1", "user-1", True),
                        ("user-group-1", "user-2", True),
                        ("user-group-1", "user-3", True),
                        ("user-group-2", "user-1", True),
                        ("user-group-2", "user-2", True),
                        ("user-group-2", "user-4", True),
                        ("user-group-3", "user-2", True),
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
            description="User Group 2 description (UPDATED)",
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
                        ("user-group-1", "User Group 1", "User Group 1 description", True),
                        (
                                "user-group-2",
                                "User Group 2 (UPDATED)",
                                "User Group 2 description (UPDATED)",
                                False,
                        ),
                        ("user-group-3", "User Group 3", "User Group 3 description", True),
                        ("user-group-4", "User Group 4", "User Group 4 description", False),
                        ("user-group-5", "User Group 5", "User Group 5 description", False),
                    ],
            ),
            (T_UG_QUERY, []),
            (
                    UGM_QUERY,
                    [
                        ("user-group-1", "user-1", True),
                        ("user-group-1", "user-2", True),
                        ("user-group-1", "user-3", True),
                        ("user-group-2", "user-1", True),
                        ("user-group-2", "user-2", False),
                        ("user-group-2", "user-4", False),
                        ("user-group-2", "user-8", True),
                        ("user-group-3", "user-2", True),
                        ("user-group-4", "user-1", True),
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
            (
                    UML_QUERY,
                    [
                        ("user-group-1", "user-1", "join"),
                        ("user-group-2", "user-2", "leave"),
                    ],
            ),
        ]:
            self.assertEqual(
                expected_value,
                self.db.retr_query(query),
                (query, expected_value),
            )

    @mock.patch("mapswipe_workers.firebase_to_postgres.update_data.auth.firebaseDB")
    def test_with_user_ids(self, fb_db_patch):
        """Test add/update users in postgres yet."""

        # Mock firebase db. Responses are simple here.
        fb_db_mock = self.FbDbMock()
        fb_db_patch.return_value = fb_db_mock

        # update user data
        update_data.create_update_user_data(
            [
                "user-1",
                "user-2",
            ]
        )
        U_QUERY = "SELECT user_id, username FROM users"
        for query, expected_value in [
            (
                    U_QUERY,
                    [
                        ("user-1", "test user"),
                        ("user-2", "test user 2"),
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
