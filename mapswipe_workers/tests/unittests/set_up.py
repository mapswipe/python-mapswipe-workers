"""Helper functions for test set up"""

import json
import os

from mapswipe_workers import auth


def set_firebase_test_data(
    data_type: str, identifier: str, project_type: str = "",
):
    test_dir = os.path.dirname(__file__)
    data_dir = os.path.join(test_dir, "data", project_type)
    file_name = data_type + ".json"
    file_path = os.path.join(data_dir, file_name)

    with open(file_path) as test_file:
        test_data = json.load(test_file)

    fb_db = auth.firebaseDB()
    ref = fb_db.reference("/v2/{0}/{1}".format(data_type, identifier))
    ref.set(test_data)


def set_postgres_test_data(data_type: str, project_type: str = "") -> None:
    test_dir = os.path.dirname(__file__)
    data_dir = os.path.join(test_dir, "data", project_type)
    file_name = data_type + ".csv"
    file_path = os.path.join(data_dir, file_name)

    pg_db = auth.postgresDB()
    with open(file_path) as f:
        pg_db.copy_from(f, data_type)


def create_test_project(project_type: str) -> str:
    """Create a test data in Firebase and Posgres."""

    project_id = "test_{0}".format(project_type)

    for data_type in ("projects", "groups", "tasks"):
        set_firebase_test_data(data_type, project_id, project_type)
        set_postgres_test_data(data_type, project_type)

    return project_id


def create_test_user() -> str:
    user_id = "test_user"
    set_firebase_test_data("users", user_id)
    return user_id


def create_test_project_draft(project_type: str) -> list:
    """
    Create test project drafts in Firebase and return project ids.
    Project drafts in Firebase are create by project manager using the dashboard.
    """
    project_id = "test_{0}".format(project_type)
    set_firebase_test_data("project_draft", project_id, project_type)
    return project_id