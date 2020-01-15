"""Helper functions for test set up"""

import os
import json

from mapswipe_workers import auth


DATA_TYPES = {
    "draft": "projectDrafts",
    "group": "groups",
    "task": "tasks",
    "result": "results",
}


def load_test_data(data_type: str, project_type: str) -> dict:
    """Load test data of given data type and project type from data directory."""
    test_dir = os.path.abspath(__file__)
    data_dir = os.path.join(test_dir, "/data/", project_type)
    file_name = data_type + ".json"
    file_path = os.path.join(data_dir, file_name)

    with open(file_path) as test_file:
        test_data = json.load(test_file)
    return test_data


def create_test_data(project_type: str) -> str:
    """Create a test data in Firebase and Posgres and return the project id."""
    fb_db = auth.firebaseDB()

    project = load_test_data("project", project_type)
    ref = fb_db.reference(f"/v2/projects/")
    project_id = ref.push(project)

    user = load_test_data("user", project_type)
    ref = fb_db.reference(f"/v2/users/")
    user_id = ref.push(user)

    for data_type in DATA_TYPES.keys():
        data = load_test_data(data_type, project_type)
        ref = fb_db.reference(f"/v2/{0}/{1}".format(DATA_TYPES[data_type], project_id))
        ref.set(data)

    return (project_id, user_id)


# TODO:
# def create_project_draft(project_type: int = 0) -> list:
#     """Create test project drafts in Firebase and return project ids."""
#     project_draft_ids = []
#     project_drafts = load_test_data("drafts", project_type)

#     fb_db = auth.firebaseDB()
#     ref = fb_db.reference(f"/v2/projectDrafts/")

#     for key, project_draft in project_drafts.items():
#         project_draft_ids.append(ref.push(project_draft))

#     return project_draft_ids
