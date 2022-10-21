import sys

from mapswipe_workers.auth import firebaseDB
from mapswipe_workers.definitions import ProjectType, logger


def get_all_projects_of_type(project_type: int, tutorial_id: str):
    """Get the project ids for active and inactive projects in Firebase DB."""

    project_id_list = []
    fb_db = firebaseDB()

    # we neglect private projects here
    # since there are no projects set up in production yet
    status_list = ["active", "inactive"]

    for status in status_list:
        logger.info(f"query {status} projects")
        projects = (
            fb_db.reference("v2/projects/")
            .order_by_child("status")
            .equal_to(status)
            .get()
        )
        for project_id, data in projects.items():
            if (data.get("projectType", 1) == project_type) & (
                data.get("tutorialId", None) == tutorial_id
            ):
                project_id_list.append(project_id)

    logger.info(f"got {len(project_id_list)} project from firebase.")
    logger.info(f"projects: {project_id_list}")
    return project_id_list


def add_tutorial_id_to_projects(project_id_list, tutorial_id):
    fb_db = firebaseDB()
    if len(project_id_list) < 1:
        logger.info("there are no matching projects.")
    else:
        for i, project_id in enumerate(project_id_list):
            fb_db.reference(f"v2/projects/{project_id}/tutorialId").set(tutorial_id)
            logger.info(
                f"#{i} added tutorial id '{tutorial_id}' to project '{project_id}'"
            )


if __name__ == "__main__":
    """change_tutorial_id_for_projects.py BUILD_AREA old_tutorial_id new_tutorial_id"""
    project_type = ProjectType[sys.argv[1]].value
    old_tutorial_id = sys.argv[2]
    new_tutorial_id = sys.argv[3]
    project_id_list = get_all_projects_of_type(project_type, old_tutorial_id)
    add_tutorial_id_to_projects(project_id_list, new_tutorial_id)
