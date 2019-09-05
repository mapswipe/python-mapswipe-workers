from firebase_admin import auth
import datetime

from mapswipe_workers.auth import firebaseDB
from mapswipe_workers.definitions import CustomError
from mapswipe_workers.definitions import logger


def set_project_manager_rights(email):
    fb_db = firebaseDB()
    try:
        user = auth.get_user_by_email(email)
        auth.set_custom_user_claims(user.uid, {'projectManager': True})
        logger.info(f'user {email} has project manager rights.')
    except Exception as e:
        logger.info(f'could not find user {email} in firebase to set project manager rights.')
        raise CustomError(e)


def remove_project_manager_rights(email):
    fb_db = firebaseDB()
    try:
        user = auth.get_user_by_email(email)
        auth.update_user(
            user.uid,
            custom_claims=auth.DELETE_ATTRIBUTE
        )
        logger.info(f'user {email} has no project manager rights.')
    except Exception as e:

        logger.info(f'could not find user {email} in firebase to remove project manager rights.')
        raise CustomError(e)


def update_username(email, username):
    fb_db = firebaseDB()
    try:
        user = auth.get_user_by_email(email)
        auth.update_user(
            user.uid,
            display_name=username
        )
        ref = fb_db.reference(f'v2/users/{user.uid}/username')
        ref.set(username)
        logger.info(f'updated username for user {email}: {username}')
    except Exception as e:
        logger.info(f'could not find user {email} in firebase to update username.')
        raise CustomError(e)


def create_user(email, username, password):
    fb_db = firebaseDB()
    try:
        user = auth.create_user(
            email=email,
            display_name=username,
            password=password
        )

        ref = fb_db.reference(f'v2/users/{user.uid}/')
        ref.update({
            'username': username,
            'taskContributionCount': 0,
            'groupContributionCount': 0,
            'projectContributionCount': 0,
            'created': datetime.datetime.utcnow().isoformat()[0:-3]+'Z' # Store current datetime in milliseconds
        })
        logger.info(f'Sucessfully created new user: {user.uid}')
    except Exception as e:
        logger.info(f'could not create new user {email}.')
        raise CustomError(e)


def delete_user(email):
    fb_db = firebaseDB()
    try:
        user = auth.get_user_by_email(email)
        ref = fb_db.reference(f'v2/users/')
        ref.update({
            user.uid: None
        })
        auth.delete_user(user.uid)
        logger.info(f'deleted user {email}')
    except Exception as e:
        logger.info(f'could not find user {email} in firebase to delete.')
        raise CustomError(e)
