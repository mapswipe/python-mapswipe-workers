import uuid
import re
from mapswipe_workers.auth import firebaseDB
from mapswipe_workers.definitions import logger, CustomError


def create_team(team_name):
    """Create new team in Firebase."""
    fb_db = firebaseDB()  # noqa E841
    try:
        # generate random uuid4 token
        team_token = str(uuid.uuid4())

        # set data in firebase
        ref = fb_db.reference(f"v2/teams/")
        team_ref = ref.push()
        team_ref.set({"teamName": team_name, "teamToken": team_token})
        logger.info(f"created team: {team_ref.key} - '{team_name}' - {team_token}")
    except Exception as e:
        logger.info(f"could not create team: {team_name}")
        raise CustomError(e)


def delete_team(team_id):
    """Delete team in Firebase."""
    # TODO: What is the consequence of this on projects and users
    #   do we expect that the teamId is removed there as well?
    fb_db = firebaseDB()  # noqa E841
    try:
        # check if team exist in firebase
        if not fb_db.reference(f"v2/teams/{team_id}").get():
            raise CustomError(f"can't find team in firebase: {team_id}")

        # get team name from firebase
        team_name = fb_db.reference(f"v2/teams/{team_id}/teamName").get()

        # check if reference path is valid, e.g. if team_id is None
        ref = fb_db.reference(f"v2/teams/{team_id}")
        if not re.match(r"/v2/\w+/[-a-zA-Z0-9]+", ref.path):
            raise CustomError(
                f"""Given argument resulted in invalid Firebase Realtime Database reference.
                        {ref.path}"""
            )

        # delete team in firebase
        ref.delete()
        logger.info(f"deleted team: {team_id} - '{team_name}'")

    except Exception as e:
        logger.info(f"could not delete team: {team_id}")
        raise CustomError(e)


def renew_team_token(team_id):
    """Create new team in Firebase."""
    fb_db = firebaseDB()  # noqa E841
    try:
        # check if team exist in firebase
        if not fb_db.reference(f"v2/teams/{team_id}").get():
            raise CustomError(f"can't find team in firebase: {team_id}")

        # get team name from firebase
        team_name = fb_db.reference(f"v2/teams/{team_id}/teamName").get()

        # check if reference path is valid
        ref = fb_db.reference(f"v2/teams/{team_id}")
        if not re.match(r"/v2/\w+/[-a-zA-Z0-9]+", ref.path):
            raise CustomError(
                f"""Given argument resulted in invalid Firebase Realtime Database reference.
                        {ref.path}"""
            )

        # generate new uuid4 token
        new_team_token = str(uuid.uuid4())

        # set team token in firebase
        ref.update({"teamToken": new_team_token})
        logger.info(f"renewed team token: {team_id} - '{team_name}' - {new_team_token}")

    except Exception as e:
        logger.info(f"could not delete team: {team_id}")
        raise CustomError(e)
