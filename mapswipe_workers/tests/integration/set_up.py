"""
Helper functions for test set up.

Directory structure of fixtures: fixtures/project_type/data_type/fixture_name
- project_type is either tile_map_service_grid or arbitrary_geometry.
- data_type is one of following: projectDrafts, projects, groups, tasks, users, results
- fixture_name is the name of the fixture file without extension. E.g. build_area
"""

import json
import os
import time
from typing import List, Union

from mapswipe_workers import auth


def set_firebase_test_data(
    project_type: str, data_type: str, fixture_name: str, identifier: str
):
    test_dir = os.path.dirname(__file__)
    fixture_name = fixture_name + ".json"
    file_path = os.path.join(
        test_dir, "fixtures", project_type, data_type, fixture_name
    )
    upload_file_to_firebase(file_path, data_type, identifier)


def upload_file_to_firebase(file_path: str, data_type: str, identifier: str):
    with open(file_path) as test_file:
        test_data = json.load(test_file)

    fb_db = auth.firebaseDB()
    ref = fb_db.reference(f"/v2/{data_type}/{identifier}")
    ref.set(test_data)


def set_postgres_test_data(
    project_type: str,
    data_type: str,
    fixture_name: str,
    columns: Union[None, List[str]] = None,
) -> None:
    test_dir = os.path.dirname(__file__)
    fixture_name = fixture_name + ".csv"
    file_path = os.path.join(
        test_dir, "fixtures", project_type, data_type, fixture_name
    )
    pg_db = auth.postgresDB()
    with open(file_path) as test_file:
        pg_db.copy_from(test_file, data_type, columns=columns)


def create_test_project(
    project_type: str,
    fixture_name: str,
    results: bool = False,
    create_user_group_session_data: bool = False,
    mapping_sessions_results: str = "mapping_sessions_results",
) -> str:
    """Create a test data in Firebase and Posgres."""
    project_id = "test_{0}".format(fixture_name)

    for data_type, columns in [
        ("projects", None),
        (
            "groups",
            [
                "project_id",
                "group_id",
                "number_of_tasks",
                "finished_count",
                "required_count",
                "progress",
                "project_type_specifics",
            ],
        ),
        ("tasks", None),
    ]:
        set_firebase_test_data(project_type, data_type, fixture_name, project_id)
        set_postgres_test_data(project_type, data_type, fixture_name, columns=columns)

    if results:
        set_firebase_test_data(project_type, "users", "user", project_id)
        set_postgres_test_data(project_type, "users", "user")
        set_firebase_test_data(project_type, "user_groups", "user_group", "")
        set_firebase_test_data(project_type, "results", fixture_name, project_id)
        set_postgres_test_data(project_type, "mapping_sessions", fixture_name)
        set_postgres_test_data(project_type, mapping_sessions_results, fixture_name)
        if create_user_group_session_data:
            set_postgres_test_data(
                project_type,
                "user_groups",
                fixture_name,
                columns=[
                    "user_group_id",
                    "name",
                    "description",
                    "is_archived",
                    "created_at",
                ],
            )
            set_postgres_test_data(project_type, "mapping_sessions_user_groups", fixture_name)

    time.sleep(5)  # Wait for Firebase Functions to complete
    return project_id


def create_test_results(project_type: str, fixture_name: str) -> str:
    """Create test results only in Firebase."""
    project_id = f"test_{project_type}"
    set_firebase_test_data(project_type, "results", fixture_name, project_id)
    time.sleep(5)  # Wait for Firebase Functions to complete
    return project_id


def create_test_user(project_type: str, user_id: str = None) -> str:
    """Create test user only in Firebase"""
    if not user_id:
        user_id = f"test_{project_type}"
    set_firebase_test_data(project_type, "users", "user", user_id)
    return user_id


def create_test_project_draft(
    project_type: str, fixture_name: str = "user", identifier: str = ""
) -> str:
    """
    Create test project drafts in Firebase and return project ids.
    Project drafts in Firebase are created by project manager using the dashboard.
    """
    if not identifier:
        identifier = f"test_{fixture_name}"
    set_firebase_test_data(project_type, "projectDrafts", fixture_name, identifier)
    return identifier


def create_test_tutorial_draft(
    project_type: str, fixture_name: str = "user", identifier: str = ""
) -> str:
    """."""
    if not identifier:
        identifier = f"test_{fixture_name}"
    set_firebase_test_data(project_type, "tutorialDrafts", fixture_name, identifier)

    return f"tutorial_{identifier}"


if __name__ == "__main__":
    create_test_project_draft("build_area")
