import sys

from mapswipe_workers.auth import firebaseDB
from mapswipe_workers.definitions import logger


def get_all_projects(organization_name: str):
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
            if data.get("requestingOrganisation", None) == organization_name:
                project_id_list.append(project_id)

    logger.info(f"got {len(project_id_list)} project from firebase.")
    logger.info(f"projects: {project_id_list}")
    return project_id_list


def update_projects(
    project_id_list, old_organization_name: str, new_organization_name: str
):
    fb_db = firebaseDB()
    if len(project_id_list) < 1:
        logger.info("there are no matching projects.")
    else:
        for i, project_id in enumerate(project_id_list):
            fb_db.reference(f"v2/projects/{project_id}/requestingOrganisation").set(
                new_organization_name
            )
            logger.info(
                f"#{i} set organization name '{new_organization_name}'"
                f"for project '{project_id}'"
            )

            project_name = fb_db.reference(f"v2/projects/{project_id}/name").get()
            new_project_name = project_name.replace(
                old_organization_name, new_organization_name
            )
            fb_db.reference(f"v2/projects/{project_id}/organizationName").set(
                new_project_name
            )
            logger.info(
                f"#{i} set project name '{new_project_name}' for project '{project_id}'"
            )


if __name__ == "__main__":
    """change_organization_name_for_projects.py old_name new_name"""
    old_organization_name = sys.argv[1]
    new_organization_name = sys.argv[2]
    project_id_list = get_all_projects(old_organization_name)
    update_projects(project_id_list, old_organization_name, new_organization_name)
