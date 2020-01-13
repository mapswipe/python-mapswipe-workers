import os
import json

from mapswipe_workers import auth
from mapswipe_workers.definitions import PROJECT_TYPE_NAMES


def load_test_project(project_type: int) -> dict:
    """Load example project from sample_data directory."""
    project_type_name = PROJECT_TYPE_NAMES[project_type]
    project_type_name = project_type_name.lower().replace(" ", "_")

    test_dir = os.path.abspath(__file__)
    data_dir = os.path.join(test_dir, "/data/")
    file_name = project_type_name + "_projects.json"
    file_path = os.path.join(data_dir, file_name)

    with open(file_path) as project_drafts_file:
        project = json.load(project_drafts_file)
    return project


def create_test_project(project_type: int) -> str:
    """Create a sample project drafts in Firebase and return project ids."""
    project = load_test_project(project_type)

    fb_db = auth.firebaseDB()
    ref = fb_db.reference(f"/v2/projects/")

    project_id = ref.push(project)

    return project_id
