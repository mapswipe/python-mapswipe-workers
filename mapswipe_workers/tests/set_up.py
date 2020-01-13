"""Helper functions for tests"""

import os
import json

from mapswipe_workers import auth
from mapswipe_workers.definitions import PROJECT_TYPE_NAMES


# DATA_TYPE_NAME = ["drafts", "project", "groups", "tasks", "results"]


def load_test_data(data_type_name: str, project_type: int) -> dict:
    """Load test data of given data type and project type from data directory."""
    project_type_name = PROJECT_TYPE_NAMES[project_type]
    project_type_name = project_type_name.lower().replace(" ", "_")

    test_dir = os.path.abspath(__file__)
    data_dir = os.path.join(test_dir, "/data/")
    file_name = project_type_name + "_" + data_type_name + ".json"
    file_path = os.path.join(data_dir, file_name)

    with open(file_path) as test_file:
        test_data = json.load(test_file)
    return test_data


def create_project_draft(project_type: int = 0) -> list:
    """Create test project drafts in Firebase and return project ids."""
    project_draft_ids = []
    project_drafts = load_test_data("drafts", project_type)

    fb_db = auth.firebaseDB()
    ref = fb_db.reference(f"/v2/projectDrafts/")

    for key, project_draft in project_drafts.items():
        project_draft_ids.append(ref.push(project_draft))

    return project_draft_ids


def create_test_project(project_type: int) -> str:
    """Create a test project in Firebase and return the project id."""
    project = load_test_data("project", project_type)

    fb_db = auth.firebaseDB()
    ref = fb_db.reference(f"/v2/projects/")

    project_id = ref.push(project)

    return project_id
