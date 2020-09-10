import sys
from mapswipe_workers.auth import firebaseDB
from mapswipe_workers.definitions import logger


def get_all_projects(project_type: int):
    """Get the user ids from all users in Firebase DB."""

    project_id_list = []
    fb_db = firebaseDB()

    status_list = ["active", "inactive"]

    for status in status_list:
        logger.info(f"query {status} projects")
        projects = (
            fb_db.reference(f"v2/projects/")
            .order_by_child("status")
            .equal_to(status)
            .get()
        )
        for project_id, data in projects.items():
            if (data.get("projectType", 1) == project_type) & (
                data.get("tutorialId", None) is None
            ):
                project_id_list.append(project_id)

    logger.info(f"got {len(project_id_list)} project from firebase.")
    return project_id_list


def add_tutorial_id_to_projects(project_id_list, tutorial_id):
    fb_db = firebaseDB()
    for project_id in project_id_list:
        fb_db.reference(f"v2/projects/{project_id}/tutorialId").set(tutorial_id)
        logger.info(f"added tutorial id '{tutorial_id}' to project '{project_id}'")


if __name__ == "__main__":
    """python add_tutorial_id_to_projects.py project_type tutorial_id"""
    project_type = sys.argv[1]
    tutorial_id = sys.argv[2]
    project_id_list = get_all_projects(1)
    add_tutorial_id_to_projects(project_id_list, tutorial_id)
