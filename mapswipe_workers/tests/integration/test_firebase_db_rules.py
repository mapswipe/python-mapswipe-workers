import json
import unittest
from requests.exceptions import HTTPError
import requests
import re
from typing import Dict
from firebase_admin.auth import UserRecord
from mapswipe_workers.config import FIREBASE_DB, FIREBASE_API_KEY
from mapswipe_workers.auth import firebaseDB
from mapswipe_workers.definitions import logger, CustomError
from mapswipe_workers.utils import user_management


def set_up_team(team_id, team_name, team_token):
    fb_db = firebaseDB()
    data = {"teamName": team_name, "teamToken": team_token}
    ref = fb_db.reference(f"v2/teams/{team_id}")
    ref.set(data)


def tear_down_team(team_id: str):
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


def tear_down_project(project_id: str):
    fb_db = firebaseDB()
    # check if reference path is valid, e.g. if team_id is None
    ref = fb_db.reference(f"v2/projects/{project_id}")
    if not re.match(r"/v2/\w+/[-a-zA-Z0-9]+", ref.path):
        raise CustomError(
            f"""Given argument resulted in invalid Firebase Realtime Database reference.
                                    {ref.path}"""
        )

    # delete team in firebase
    ref.delete()


def setup_user(
    project_manager: bool, team_member: bool, team_id: str = ""
) -> UserRecord:
    if project_manager and team_member:
        username = f"unittest-project-manager-and-team-member"
    elif project_manager:
        username = f"unittest-project-manager"
    elif team_member:
        username = f"unittest-team-member"
    else:
        username = f"unittest-normal-user"

    email = f"{username}@mapswipe.org"
    password = f"{username}_pw"

    # username will be user.display_name
    user = user_management.create_user(email, username, password)

    # set project manager credentials
    if project_manager:
        user_management.set_project_manager_rights(email)

    # set team member attribute
    if team_member:
        user_management.add_user_to_team(email, team_id)

    return user


def sign_in_with_email_and_password(email: str, password: str) -> Dict:
    request_ref = (
        f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword"
        f"?key={FIREBASE_API_KEY}"
    )
    headers = {"content-type": "application/json; charset=UTF-8"}
    data = json.dumps({"email": email, "password": password, "returnSecureToken": True})
    request_object = requests.post(request_ref, headers=headers, data=data)
    current_user = request_object.json()
    logger.info(f"signed in with user {email}")
    return current_user


def permission_denied(request_object: requests.Response):
    try:
        request_object.raise_for_status()
    except HTTPError as e:
        if "Permission denied" in request_object.text:
            return True
        else:
            raise HTTPError(e, request_object.text)


def test_get_endpoint(user: dict, path: str, custom_arguments: str = ""):
    database_url = f"https://{FIREBASE_DB}.firebaseio.com"
    request_ref = f"{database_url}{path}.json?{custom_arguments}&auth={user['idToken']}"
    headers = {"content-type": "application/json; charset=UTF-8"}
    request_object = requests.get(request_ref, headers=headers)
    if permission_denied(request_object):
        logger.info(
            f"permission denied for {database_url}{path}.json?{custom_arguments}"
        )
        return False
    else:
        logger.info(
            f"permission granted for {database_url}{path}.json?{custom_arguments}"
        )
        return True


def test_set_endpoint(user: dict, path: str):
    data = {"test_key": "test_value"}
    database_url = f"https://{FIREBASE_DB}.firebaseio.com"
    request_ref = f"{database_url}{path}.json?auth={user['idToken']}"
    headers = {"content-type": "application/json; charset=UTF-8"}
    request_object = requests.put(
        request_ref, headers=headers, data=json.dumps(data).encode("utf-8")
    )
    if permission_denied(request_object):
        logger.info(f"permission denied for {database_url}{path}.json")
        return False
    else:
        logger.info(f"permission granted for  for {database_url}{path}.json")
        return True


class TestFirebaseDBRules(unittest.TestCase):
    def setUp(self):

        # setup team
        self.team_id = "unittest-team-1234"
        self.team_name = "unittest-team"
        self.team_token = "12345678-1234-5678-1234-567812345678"
        set_up_team(self.team_id, self.team_name, self.team_token)

        # setup team b
        self.team_id_b = "unittest-team-1234-b"
        self.team_name_b = "unittest-team-b"
        self.team_token_b = "12345678-1234-5678-1234-567812345678"
        set_up_team(self.team_id_b, self.team_name_b, self.team_token_b)

        # setup public project
        self.public_project_id = "unittest-public-project"
        fb_db = firebaseDB()
        ref = fb_db.reference(f"v2/projects/{self.public_project_id}")
        ref.update({"status": "active"})

        # setup private project team a
        self.private_project_id = "unittest-private-project"
        fb_db = firebaseDB()
        ref = fb_db.reference(f"v2/projects/{self.private_project_id}")
        ref.update({"teamId": self.team_id, "status": "private_active"})

        # setup private project team b
        self.private_project_id_b = "unittest-private-project-b"
        fb_db = firebaseDB()
        ref = fb_db.reference(f"v2/projects/{self.private_project_id_b}")
        ref.update({"teamId": self.team_id_b, "status": "private_active"})

        # setup users
        self.normal_user = setup_user(project_manager=False, team_member=False)
        self.team_member = setup_user(
            project_manager=False, team_member=True, team_id=self.team_id
        )
        self.project_manager = setup_user(project_manager=True, team_member=False)

        # generate all endpoints to test
        self.endpoints = [  # [path, custom_arguments]
            # projects
            [f"/v2/projects", f'orderBy="status"&equalTo="active"&limitToFirst=20'],
            [f"/v2/projects/{self.public_project_id}/status", ""],
            [
                f"/v2/projects",
                f'orderBy="teamId"&equalTo="{self.team_id}"&limitToFirst=20',
            ],
            [f"/v2/projects/{self.private_project_id}/status", ""],
            [
                f"/v2/projects",
                f'orderBy="teamId"&equalTo="{self.team_id_b}"&limitToFirst=20',
            ],
            [f"/v2/projects/{self.private_project_id_b}/status", ""],
            # teams
            [f"/v2/teams/{self.team_id}", ""],
            [f"/v2/teams/{self.team_id}/teamName", ""],
            [f"/v2/teams/{self.team_id}/teamToken", ""],
            # groups
            [f"/v2/groups/{self.public_project_id}", ""],
            [f"/v2/groups/{self.private_project_id}", ""],
            # tasks
            [f"/v2/tasks/{self.public_project_id}", ""],
            [f"/v2/tasks/{self.private_project_id}", ""],
            # users
            [f"/v2/users/<user_id>", ""],
            [f"/v2/users/<user_id>/teamId", ""],
            [f"/v2/users/<user_id>/username", ""],
            # results
            [f"/v2/results/{self.public_project_id}/<group_id>/<user_id>", ""],
            [f"/v2/results/{self.private_project_id}/<group_id>/<user_id>", ""],
        ]

    def tearDown(self):
        # tear down team
        tear_down_team(self.team_id)
        tear_down_team(self.team_id_b)

        # tear down users
        user_management.delete_user(self.normal_user.email)
        user_management.delete_user(self.team_member.email)
        user_management.delete_user(self.project_manager.email)

        # tear down public / private project
        tear_down_project(self.public_project_id)
        tear_down_project(self.private_project_id)
        tear_down_project(self.private_project_id_b)

    def test_access_as_normal_user(self):
        # sign in user with email and password to simulate app user
        user = sign_in_with_email_and_password(
            self.normal_user.email, f"{self.normal_user.display_name}_pw"
        )

        expected_access = [  # [read, write]
            (True, False),  # public project query
            (True, False),  # public project status attribute
            (False, False),  # private project query
            (False, False),  # private project status attribute
            (False, False),  # private project b query
            (False, False),  # private project b status attribute
            (False, False),  # team
            (False, False),  # teamName
            (False, False),  # teamToken
            (True, False),  # public group
            (False, False),  # private group
            (True, False),  # public task
            (False, False),  # private task
            (True, False),  # user
            (True, False),  # user teamId
            (True, True),  # user username
            (False, True),  # results public project
            (False, False),  # results private project
        ]
        for i, endpoint in enumerate(self.endpoints):
            path = endpoint[0].replace("<user_id>", user["localId"])
            custom_arguments = endpoint[1]
            read_access = test_get_endpoint(user, path, custom_arguments)
            self.assertEqual(
                read_access,
                expected_access[i][0],
                f"observed, expected, get {endpoint} {user['displayName']}",
            )
            write_access = test_set_endpoint(user, path)
            self.assertEqual(
                write_access,
                expected_access[i][1],
                f"observed, expected, set {endpoint} {user['displayName']}",
            )

    def test_access_as_team_member(self):
        # sign in user with email and password to simulate app user
        user = sign_in_with_email_and_password(
            self.team_member.email, f"{self.team_member.display_name}_pw"
        )

        expected_access = [  # [read, write]
            (True, False),  # public project query
            (True, False),  # public project status attribute
            (True, False),  # private project query
            (True, False),  # private project status
            (False, False),  # private project b query
            (False, False),  # private project b status
            (False, False),  # team
            (True, False),  # teamName
            (False, False),  # teamToken
            (True, False),  # public group
            (True, False),  # private group
            (True, False),  # public task
            (True, False),  # private task
            (True, False),  # user
            (True, False),  # user teamId
            (True, True),  # user username
            (False, True),  # results public project
            (False, True),  # results private project
        ]

        for i, endpoint in enumerate(self.endpoints):
            path = endpoint[0].replace("<user_id>", user["localId"])
            custom_arguments = endpoint[1]
            read_access = test_get_endpoint(user, path, custom_arguments)
            self.assertEqual(
                read_access,
                expected_access[i][0],
                f"observed, expected, get {endpoint} {user['displayName']}",
            )
            write_access = test_set_endpoint(user, path)
            self.assertEqual(
                write_access,
                expected_access[i][1],
                f"observed, expected, set {endpoint} {user['displayName']}",
            )

    def test_access_as_project_manager(self):
        # sign in user with email and password to simulate app user
        user = sign_in_with_email_and_password(
            self.project_manager.email, f"{self.project_manager.display_name}_pw"
        )

        expected_access = [  # [read, write]
            (True, False),  # public project query
            (True, True),  # public project status attribute
            (True, False),  # private project query
            (True, True),  # private project status
            (True, False),  # private project b query
            (True, True),  # private project b status
            (True, True),  # team
            (True, True),  # teamName
            (True, True),  # teamToken
            (True, False),  # public group
            (True, False),  # private group
            (True, False),  # public task
            (True, False),  # private task
            (True, False),  # user
            (True, False),  # user teamId
            (True, True),  # user username
            (False, True),  # results public project
            (False, False),  # results private project
        ]

        for i, endpoint in enumerate(self.endpoints):
            path = endpoint[0].replace("<user_id>", user["localId"])
            custom_arguments = endpoint[1]
            read_access = test_get_endpoint(user, path, custom_arguments)
            self.assertEqual(
                read_access,
                expected_access[i][0],
                f"observed, expected, get {endpoint} {user['displayName']}",
            )
            write_access = test_set_endpoint(user, path)
            self.assertEqual(
                write_access,
                expected_access[i][1],
                f"observed, expected, set {endpoint} {user['displayName']}",
            )


if __name__ == "__main__":
    unittest.main()
