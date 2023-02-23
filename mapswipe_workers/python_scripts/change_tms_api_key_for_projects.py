import sys

from mapswipe_workers.auth import firebaseDB
from mapswipe_workers.config import IMAGE_API_KEYS
from mapswipe_workers.definitions import ProjectType, logger


def get_all_projects_by_tms(tms_name: str):
    """Get the project ids for active and inactive projects in Firebase DB."""

    project_id_list = []
    fb_db = firebaseDB()

    # we neglect private projects here
    # since there are no projects set up in production yet
    status_list = ["active", "inactive", "tutorial"]

    for status in status_list:
        logger.info(f"query {status} projects")
        projects = (
            fb_db.reference("v2/projects/")
            .order_by_child("status")
            .equal_to(status)
            .get()
        )
        for project_id, data in projects.items():
            project_type = data.get("projectType", None)

            # build area, footprint and completeness project types
            # use a single tile server for satellite imagery
            if (
                project_type
                in [
                    ProjectType.BUILD_AREA.value,
                    ProjectType.FOOTPRINT.value,
                    ProjectType.COMPLETENESS.value,
                ]
                and data["tileServer"]["name"] == tms_name
            ):
                project_id_list.append(project_id)

    logger.info(f"got {len(project_id_list)} project from firebase.")
    logger.info(f"projects: {project_id_list}")
    return project_id_list


def add_api_key_to_projects(project_id_list, api_key):
    fb_db = firebaseDB()
    if len(project_id_list) < 1:
        logger.info("there are no matching projects.")
    else:
        for i, project_id in enumerate(project_id_list):
            fb_db.reference(f"v2/projects/{project_id}/tileServer/apiKey").set(api_key)
            logger.info(f"#{i+1} added api key '{api_key}' to project '{project_id}'")


if __name__ == "__main__":
    """change_tms_api_key_for_projects.py maxar_premium"""
    logger.info(
        "This script currently supports only the following project types:"
        "build_area, footprint, completeness. "
        "The new api key will be obtained from the .env file. "
        "Make sure to update this file first."
    )

    try:
        tms_name = sys.argv[1]
        if tms_name in IMAGE_API_KEYS.keys():
            new_api_key = IMAGE_API_KEYS[tms_name]
            project_id_list = get_all_projects_by_tms(tms_name)
            add_api_key_to_projects(project_id_list, new_api_key)
        else:
            logger.info(
                f"'{tms_name}' is not a valid TMS provider name. "
                f"Valid options are: {list(IMAGE_API_KEYS.keys())}"
            )
    except IndexError:
        logger.info(
            "Provide a valid TMS provider name as an argument to this script. "
            f"Valid options are: {list(IMAGE_API_KEYS.keys())}"
        )
