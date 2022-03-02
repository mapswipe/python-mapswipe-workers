from mapswipe_workers.auth import firebaseDB
from mapswipe_workers.definitions import MessageType, logger
from mapswipe_workers.utils.slack_helper import send_slack_message


def get_projects(status):
    """Load 'active' projects from Firebase."""
    fb_db = firebaseDB()
    projects = (
        fb_db.reference("v2/projects/").order_by_child("status").equal_to(status).get()
    )
    logger.info(f"got {len(projects)} {status} projects from firebase")
    return projects


def filter_projects_by_name_and_progress(projects, filter_string, progress_threshold):
    """Load 'active' projects from Firebase."""
    selected_project_ids = []
    for project_id in projects.keys():
        name = projects[project_id]["name"]
        progress = projects[project_id]["progress"]
        if filter_string in name and progress >= progress_threshold:
            selected_project_ids.append(project_id)

    logger.info(
        f"selected {len(selected_project_ids)} project(s) which contain(s) "
        f"'{filter_string}' in the project name and progress >= {progress_threshold}%."
    )
    return selected_project_ids


def set_status_in_firebase(project_id, project_name, new_status):
    """Change status of a project in Firebase."""
    # change status in firebase
    fb_db = firebaseDB()
    fb_db.reference(f"v2/projects/{project_id}/status").set(new_status)
    logger.info(f"set project status to '{new_status}' for project {project_id}")

    # send slack message
    if new_status == "finished":
        send_slack_message(
            MessageType.PROJECT_STATUS_FINISHED, project_name, project_id
        )
    elif new_status == "active":
        send_slack_message(MessageType.PROJECT_STATUS_ACTIVE, project_name, project_id)


if __name__ == "__main__":
    """Check if project status should be updated and change value in Firebase."""
    filter_string = "Test"

    active_projects = get_projects(status="active")
    finished_projects = filter_projects_by_name_and_progress(
        active_projects, filter_string, progress_threshold=1,
    )

    inactive_projects = get_projects(status="inactive")
    new_active_projects = filter_projects_by_name_and_progress(
        inactive_projects, filter_string, progress_threshold=0,
    )[0 : len(finished_projects)]

    if len(new_active_projects) > 0:
        for project_id in finished_projects:
            project_name = active_projects[project_id]["name"]
            set_status_in_firebase(project_id, project_name, new_status="finished")

        for project_id in new_active_projects:
            project_name = inactive_projects[project_id]["name"]
            set_status_in_firebase(project_id, project_name, new_status="active")
