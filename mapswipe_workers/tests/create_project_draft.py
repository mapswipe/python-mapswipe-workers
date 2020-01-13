import os
import json

from mapswipe_workers import auth
from mapswipe_workers.definitions import PROJECT_TYPE_NAMES


def load_sample_project_drafts(project_type: int) -> dict:
    """Load example project drafts of given project type from template."""
    project_type_name = PROJECT_TYPE_NAMES[project_type]
    project_type_name = project_type_name.lower().replace(" ", "_")

    test_dir = os.path.abspath(__file__)
    data_dir = os.path.join(test_dir, "/data/")
    file_name = project_type_name + "_drafts.json"
    file_path = os.path.join(data_dir, file_name)

    with open(file_path) as project_drafts_file:
        project_drafts = json.load(project_drafts_file)
    return project_drafts


def create_project_draft(project_type: int = 0) -> list:
    """Create a sample project drafts in Firebase and return project ids."""
    project_draft_ids = []
    project_drafts = load_sample_project_drafts(project_type)

    fb_db = auth.firebaseDB()
    ref = fb_db.reference(f"/v2/projectDrafts/")

    for key, project_draft in project_drafts.items():
        project_draft_ids.append(ref.push(project_draft))

    return project_draft_ids
