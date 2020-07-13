import unittest
import re
from mapswipe_workers.utils import team_management
from mapswipe_workers.auth import firebaseDB
from mapswipe_workers.definitions import CustomError


def set_up_team():
    fb_db = firebaseDB()
    team_id = "unittest-team-1234"
    team_name = "unittest-team"
    team_token = "12345678-1234-5678-1234-567812345678"
    data = {"teamName": team_name, "teamToken": team_token}
    ref = fb_db.reference(f"v2/teams/{team_id}")
    ref.set(data)

    return team_id, team_name, team_token


def set_up_team_member():
    fb_db = firebaseDB()
    team_id = "unittest-team-1234"
    user_id = "unittest-team-member-1"
    data = {"teamId": team_id}
    ref = fb_db.reference(f"v2/users/{user_id}")
    ref.set(data)

    return user_id


def tear_down_team(team_id):
    fb_db = firebaseDB()
    # check if reference path is valid, e.g. if team_id is None
    ref = fb_db.reference(f"v2/teams/{team_id}")
    if not re.match(r"/v2/\w+/[-a-zA-Z0-9]+", ref.path):
        raise CustomError(
            f"""Given argument resulted in invalid Firebase Realtime Database reference.
                                    {ref.path}"""
        )

    # delete team in firebase
    ref.delete()


def tear_down_team_member(user_id):
    fb_db = firebaseDB()
    # check if reference path is valid, e.g. if team_id is None
    ref = fb_db.reference(f"v2/users/{user_id}")
    if not re.match(r"/v2/\w+/[-a-zA-Z0-9]+", ref.path):
        raise CustomError(
            f"""Given argument resulted in invalid Firebase Realtime Database reference.
                                    {ref.path}"""
        )

    # delete team in firebase
    ref.delete()


class TestTeamManagement(unittest.TestCase):
    def setUp(self):
        self.team_id, self.team_name, self.team_token = set_up_team()
        self.user_id = set_up_team_member()

    def tearDown(self):
        tear_down_team(self.team_id)
        tear_down_team_member(self.user_id)

    def test_create_team(self):
        self.team_name = "unittest-team"
        self.team_id, self.team_token = team_management.create_team(self.team_name)

        # check if returned values are plausible
        self.assertIsNotNone(self.team_id)
        self.assertGreaterEqual(len(self.team_token), 32)

        # check data in Firebase
        fb_db = firebaseDB()
        ref = fb_db.reference(f"v2/teams/{self.team_id}")
        team_data = ref.get()
        self.assertEqual(len(team_data), 2)
        self.assertEqual(team_data["teamName"], self.team_name)
        self.assertEqual(team_data["teamToken"], self.team_token)

    def test_delete_team(self):
        team_management.delete_team(self.team_id)

        # check if no data in Firebase
        fb_db = firebaseDB()
        ref = fb_db.reference(f"v2/teams/{self.team_id}")
        team_data = ref.get()
        self.assertIsNone(team_data)

        # check if no members
        team_members = (
            fb_db.reference(f"v2/users/")
            .order_by_child("teamId")
            .equal_to(self.team_id)
            .get()
        )
        self.assertEqual(len(team_members), 0)

    def test_renew_team_token(self):
        new_team_token = team_management.renew_team_token(self.team_id)

        self.assertGreaterEqual(len(new_team_token), 32)
        self.assertNotEqual(new_team_token, self.team_token)

    def test_remove_all_team_members(self):
        team_management.remove_all_team_members(self.team_id)

        # check if no members
        fb_db = firebaseDB()
        team_members = (
            fb_db.reference(f"v2/users/")
            .order_by_child("teamId")
            .equal_to(self.team_id)
            .get()
        )
        self.assertEqual(len(team_members), 0)


if __name__ == "__main__":
    unittest.main()
