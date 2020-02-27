"""Helper functions for test set up"""

import json
import os

from mapswipe_workers import auth

DATA_TYPES = {
    "group": "groups",
    "task": "tasks",
    # "result": "results",
}


def load_test_data(data_type: str, project_type: str = "") -> dict:
    """Load test data of given data type and project type from data directory."""
    test_dir = os.path.dirname(__file__)
    data_dir = os.path.join(test_dir, "data", project_type)
    file_name = data_type + ".json"
    file_path = os.path.join(data_dir, file_name)

    with open(file_path) as test_file:
        test_data = json.load(test_file)
    return test_data


def create_test_project(project_type: str) -> str:
    """Create a test data in Firebase and Posgres and return the project id."""
    project = load_test_data("project", project_type)

    fb_db = auth.firebaseDB()
    ref = fb_db.reference("/v2/projects/")
    project_id = ref.push(project).key

    for data_type in DATA_TYPES.keys():
        data = load_test_data(data_type, project_type)
        ref = fb_db.reference("/v2/{0}/{1}".format(data_type, project_id))
        ref.set(data)

    # TODO: Create test project also in Postgres

    return project_id


def create_test_user() -> str:
    user = load_test_data("user")

    fb_db = auth.firebaseDB()
    ref = fb_db.reference("/v2/users/")
    user_id = ref.push(user).key

    return user_id


def create_test_project_draft(project_type: str) -> list:
    """Create test project drafts in Firebase and return project ids."""
    project_draft = load_test_data("project_draft", project_type)

    fb_db = auth.firebaseDB()
    ref = fb_db.reference("/v2/projectDrafts/")
    project_id = ref.push(project_draft).key

    return project_id
