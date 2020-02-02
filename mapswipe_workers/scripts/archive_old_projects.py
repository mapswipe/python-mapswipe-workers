from mapswipe_workers import auth
from mapswipe_workers.definitions import logger


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


def move_project_data_to_v2(project_id, project_data):
    """
    Copy project information from old path to v2/projects in Firebase.
    Add status=archived attribute.
    """
    project_data["status"] = "archived"
    fb_db = auth.firebaseDB()
    fb_db.reference("v2/projects/{0}".format(project_id)).set(project_data)
    fb_db.reference("projects/{0}".format(project_id)).set({})
    logger.info(f"moved old project to v2: {project_id}")


def delete_old_groups(project_id):
    """
    Delete old groups for a project
    """
    fb_db = auth.firebaseDB()
    fb_db.reference("groups/{0}".format(project_id)).set({})
    logger.info(f"deleted groups for: {project_id}")


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
        project_data = projects[project_id]
        move_project_data_to_v2(project_id, project_data)
        delete_old_groups(project_id)

    delete_other_old_data()


archive_old_projects()
