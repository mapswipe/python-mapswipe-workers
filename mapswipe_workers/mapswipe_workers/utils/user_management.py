import datetime
import json

import requests
from firebase_admin import auth
from requests.exceptions import HTTPError

from mapswipe_workers.auth import firebaseDB
from mapswipe_workers.config import FIREBASE_API_KEY, FIREBASE_DB
from mapswipe_workers.definitions import CustomError, logger


def set_project_manager_rights(email):
    fb_db = firebaseDB()  # noqa E841
    try:
        user = auth.get_user_by_email(email)
        auth.set_custom_user_claims(user.uid, {"projectManager": True})
        logger.info(f"user {email} has project manager rights.")
    except Exception as e:
        logger.info(
            f"could not find user {email} in firebase to set project manager rights."
        )
        raise CustomError(e)


def remove_project_manager_rights(email):
    fb_db = firebaseDB()  # noqa E841
    try:
        user = auth.get_user_by_email(email)
        auth.update_user(user.uid, custom_claims=auth.DELETE_ATTRIBUTE)
        logger.info(f"user {email} has no project manager rights.")
    except Exception as e:

        logger.info(
            f"could not find user {email} in firebase to remove project manager rights."
        )
        raise CustomError(e)


def list_all_project_managers():
    fb_db = firebaseDB()  # noqa E841
    page = auth.list_users()
    while page:
        for user in page.users:
            if user.custom_claims:
                print("User: " + user.uid + " " + user.email)
        # Get next batch of users.
        page = page.get_next_page()


def update_username(email, username):
    fb_db = firebaseDB()
    try:
        user = auth.get_user_by_email(email)
        auth.update_user(user.uid, display_name=username)
        ref = fb_db.reference(f"v2/users/{user.uid}/username")
        ref.set(username)
        logger.info(f"updated username for user {email}: {username}")
    except Exception as e:
        logger.info(f"could not find user {email} in firebase to update username.")
        raise CustomError(e)


def create_user(email, username, password):
    fb_db = firebaseDB()
    try:
        user = auth.create_user(email=email, display_name=username, password=password)

        ref = fb_db.reference(f"v2/users/{user.uid}/")
        ref.update(
            {
                "username": username,
                "taskContributionCount": 0,
                "groupContributionCount": 0,
                "projectContributionCount": 0,
                "created": datetime.datetime.utcnow().isoformat()[0:-3]
                + "Z",  # Store current datetime in milliseconds
            }
        )
        logger.info(f"created new user: {user.uid}")
        return user
    except Exception as e:
        logger.info(f"could not create new user {email}.")
        raise CustomError(e)


def delete_user(email):
    fb_db = firebaseDB()
    try:
        user = auth.get_user_by_email(email)
        ref = fb_db.reference("v2/users/")
        ref.update({user.uid: None})
        auth.delete_user(user.uid)
        logger.info(f"deleted user {email}")
    except Exception as e:
        logger.info(f"could not find user {email} in firebase to delete.")
        raise CustomError(e)


def sign_in_with_email_and_password(email, password):
    api_key = FIREBASE_API_KEY
    request_ref = (
        "https://www.googleapis.com/identitytoolkit/"
        + "v3/relyingparty/verifyPassword?key={0}".format(api_key)
    )
    headers = {"content-type": "application/json; charset=UTF-8"}
    data = json.dumps({"email": email, "password": password, "returnSecureToken": True})
    request_object = requests.post(request_ref, headers=headers, data=data)
    current_user = request_object.json()
    logger.info(f"signed in with user {email}")
    return current_user


def get_firebase_db(path, custom_arguments=None, token=None):
    database_name = FIREBASE_DB
    database_url = f"https://{database_name}.firebaseio.com"
    request_ref = "{0}{1}.json?{3}auth={2}".format(
        database_url, path, token, custom_arguments
    )
    headers = {"content-type": "application/json; charset=UTF-8"}
    request_object = requests.get(request_ref, headers=headers)
    if permission_denied(request_object):
        logger.info(f"permission denied for {database_url}{path}.json")
        return False
    else:
        logger.info(
            f"get data in firebase for {database_url}{path}.json?{custom_arguments}"
        )
        return request_object.json()


def set_firebase_db(path, data, token=None):
    database_name = FIREBASE_DB
    database_url = f"https://{database_name}.firebaseio.com"
    request_ref = "{0}{1}.json?auth={2}".format(database_url, path, token)
    headers = {"content-type": "application/json; charset=UTF-8"}
    request_object = requests.put(
        request_ref, headers=headers, data=json.dumps(data).encode("utf-8")
    )
    if permission_denied(request_object):
        logger.info(f"permission denied for {database_url}{path}.json")
        return False
    else:
        logger.info(f"set data in firebase for {database_url}{path}.json")
        return request_object.json()


def update_firebase_db(path, data, token=None):
    database_name = FIREBASE_DB
    database_url = f"https://{database_name}.firebaseio.com"
    request_ref = "{0}{1}.json?auth={2}".format(database_url, path, token)
    headers = {"content-type": "application/json; charset=UTF-8"}
    request_object = requests.patch(
        request_ref, headers=headers, data=json.dumps(data).encode("utf-8")
    )
    if permission_denied(request_object):
        logger.info(f"permission denied for {database_url}{path}.json")
        return False
    else:
        logger.info(f"updated data in firebase for {database_url}{path}.json")
        return request_object.json()


def permission_denied(request_object):
    try:
        request_object.raise_for_status()
    except HTTPError as e:
        if "Permission denied" in request_object.text:
            return True
        else:
            raise HTTPError(e, request_object.text)


def add_user_to_team(email, team_id):
    """Add teamId attribute for user."""
    try:
        fb_db = firebaseDB()  # noqa E841

        # check if team exist in firebase
        if not fb_db.reference(f"v2/teams/{team_id}").get():
            raise CustomError(f"can't find team in firebase: {team_id}")

        # get user by email
        try:
            user = auth.get_user_by_email(email)
        except auth.UserNotFoundError:
            raise CustomError(f"can't find user in firebase: {email}")

        # set teamId attribute for user in firebase
        ref = fb_db.reference(f"v2/users/{user.uid}")
        ref.update({"teamId": team_id})
        logger.info(f"added teamId {team_id} for user {email} - {user.uid}.")

    except Exception as e:
        logger.info("could not add teamId attribute for user.")
        raise CustomError(e)


def remove_user_from_team(email):
    """Remove teamId attribute for user."""
    try:
        fb_db = firebaseDB()  # noqa E841

        # get user by email
        try:
            user = auth.get_user_by_email(email)
        except auth.UserNotFoundError:
            raise CustomError(f"can't find user in firebase: {email}")

        # get teamId from firebase
        team_id = fb_db.reference(f"v2/users/{user.uid}/teamId").get()

        # remove teamId attribute for user in firebase
        ref = fb_db.reference(f"v2/users/{user.uid}")
        ref.update({"teamId": None})  # deletes the teamId attribute in firebase
        logger.info(f"removed teamId {team_id} for user {email} - {user.uid}.")

    except Exception as e:
        logger.info("could not remove teamId attribute for user.")
        raise CustomError(e)
