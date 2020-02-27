"""Helper functions for test set up"""

import json
import os

from mapswipe_workers import auth


def load_firebase_test_data(data_type: str, project_type: str = "") -> dict:
    """Load test data of given data type and project type from data directory."""
    test_dir = os.path.dirname(__file__)
    data_dir = os.path.join(test_dir, "data", project_type)
    file_name = data_type + ".json"
    file_path = os.path.join(data_dir, file_name)

    with open(file_path) as test_file:
        test_data = json.load(test_file)
    return test_data


def set_postgres_test_data(data_type: str, project_type: str = "") -> None:
    test_dir = os.path.dirname(__file__)
    data_dir = os.path.join(test_dir, "data", project_type)
    file_name = data_type + ".csv"
    file_path = os.path.join(data_dir, file_name)

    pg_db = auth.postgresDB()
    with open(file_path) as f:
        pg_db.copy_from(f, data_type)


def create_test_project(project_type: str) -> str:
    """Create a test data in Firebase and Posgres and return the project id."""
    project = load_firebase_test_data("projects", project_type)
    project_id = project["projectId"]

    fb_db = auth.firebaseDB()

    for data_type in ("projects", "groups", "tasks"):
        data = load_firebase_test_data(data_type, project_type)
        ref = fb_db.reference("/v2/{0}/{1}".format(data_type, project_id))
        ref.set(data)
        set_postgres_test_data(data_type, project_type)

    return project_id


def create_test_user() -> str:
    user = load_firebase_test_data("user")

    fb_db = auth.firebaseDB()
    ref = fb_db.reference("/v2/users/")
    user_id = ref.push(user).key

    return user_id


def create_test_project_draft(project_type: str) -> list:
    """Create test project drafts in Firebase and return project ids."""
    project_draft = load_firebase_test_data("project_draft", project_type)

    fb_db = auth.firebaseDB()
    ref = fb_db.reference("/v2/projectDrafts/")
    project_id = ref.push(project_draft).key

    return project_id
