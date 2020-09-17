import re
from typing import Iterable

from firebase_admin import exceptions

from mapswipe_workers import auth
from mapswipe_workers.definitions import CustomError, logger


def chunks(data: list, size: int = 250) -> Iterable[list]:
    """Yield successive n-sized chunks from list."""
    for i in range(0, len(data), size):
        yield data[i : i + size]  # noqa E203


def get_old_groups():
    """
    Get all projects from Firebase which have been created
    before we switched to v2.
    """
    fb_db = auth.firebaseDB()
    ref = fb_db.reference("groups")
    projects = ref.get(shallow=True)
    logger.info("got old projects from firebase")
    return projects


def move_project_data_to_v2(project_id):
    """
    Copy project information from old path to v2/projects in Firebase.
    Add status=archived attribute.
    Use Firebase transaction function for this.
    """

    # Firebase transaction function
    def transfer(current_data):
        # we need to add these attributes
        # since they are expected for version 2
        current_data["status"] = "archived"
        current_data["projectType"] = 1
        current_data["projectId"] = str(project_id)
        current_data["progress"] = current_data.get("progress", 0)
        current_data["name"] = current_data.get("name", "unknown")
        fb_db.reference("v2/projects/{0}".format(project_id)).set(current_data)
        return dict()

    fb_db = auth.firebaseDB()
    projects_ref = fb_db.reference(f"projects/{project_id}")
    try:
        projects_ref.transaction(transfer)
        logger.info(f"{project_id}: Transfered project to v2 and delete in old path")
        return True
    except fb_db.TransactionAbortedError:
        logger.exception(
            f"{project_id}: Firebase transaction"
            f"for transferring project failed to commit"
        )
        return False


def delete_old_groups(project_id):
    """
    Delete old groups for a project
    """
    fb_db = auth.firebaseDB()
    ref = fb_db.reference(f"/groups/{project_id}")
    if not re.match(r"/\w+/[-a-zA-Z0-9]+", ref.path):
        raise CustomError(
            f"""Given argument resulted in invalid Firebase Realtime Database reference.
                    {ref.path}"""
        )
    try:
        ref.delete()
    except exceptions.InvalidArgumentError:
        # Data to write exceeds the maximum size that can be modified
        # with a single request. Delete chunks of data instead.
        childs = ref.get(shallow=True)
        for chunk in chunks(list(childs.keys())):
            ref.update({key: None for key in chunk})
        ref.delete()


def run_delete_old_groups():
    """
    Run workflow to delete old groups.
    First get all old project ids from remaining groups.
    Then delete all groups for the given project_ids.
    """

    projects = get_old_groups()
    for project_id in projects:
        delete_old_groups(project_id)
        logger.info(f"{project_id}: deleted old groups")


run_delete_old_groups()
