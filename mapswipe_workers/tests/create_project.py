import os
import json

from mapswipe_workers import auth


def load_sample_project(project_type: int) -> dict:
    """Load example project from sample_data directory."""
    # TODO: Differentiate between project_types.
    test_dir = os.path.abspath(__file__)
    sample_data_dir = os.path.join(test_dir, "/sample_data/")
    sample_file_name = "test_project.json"
    sample_file_path = os.path.join(sample_data_dir, sample_file_name)

    with open(sample_file_path) as sample_project_drafts_file:
        sample_project_drafts = json.load(sample_project_drafts_file)
    return sample_project_drafts


def create_project(project_type: int = 0) -> str:
    """Create a sample project drafts in Firebase and return project ids."""
    project_draft = load_sample_project(project_type)

    fb_db = auth.firebaseDB()
    ref = fb_db.reference(f"/v2/projects/")

    project_id = ref.push(project_draft)

    return project_id
