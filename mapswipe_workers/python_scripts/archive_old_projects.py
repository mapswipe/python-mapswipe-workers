from mapswipe_workers import auth
from mapswipe_workers.definitions import logger, CustomError
from typing import Iterable
import re
from firebase_admin import exceptions


def chunks(data: list, size: int = 250) -> Iterable[list]:
    """Yield successive n-sized chunks from list."""
    for i in range(0, len(data), size):
        yield data[i : i + size]  # noqa E203


def get_old_projects():
    """
    Get all projects from Firebase which have been created
    before we switched to v2.
    """
    fb_db = auth.firebaseDB()
    ref = fb_db.reference("projects")
    projects = ref.get()
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


def delete_other_old_data():
    """
    Delete old imports, results, announcements in Firebase
    """
    fb_db = auth.firebaseDB()
    fb_db.reference("imports").set({})
    fb_db.reference("results").set({})
    fb_db.reference("announcements").set({})
    logger.info(f"deleted old results, imports, announcements")


def archive_old_projects():
    """
    Run workflow to archive old projects.
    First get all old projects.
    Move project data to v2/projects in Firebase and
    set status=archived.
    Then delete all groups for a project.
    Finally, delete old results, imports and announcements.
    We don't touch the old user data in this workflow.
    """

    projects = get_old_projects()
    for project_id in projects.keys():
        if move_project_data_to_v2(project_id):
            delete_old_groups(project_id)
        else:
            logger.info(f"didn't delete project and groups for project: {project_id}")

    delete_other_old_data()


archive_old_projects()
