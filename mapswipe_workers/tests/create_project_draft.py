import os
import json

from mapswipe_workers import auth


def load_sample_project_drafts(project_type: int) -> dict:
    """Load example project drafts of given project type from test/sample_data directory."""
    project_types = {
        1: "build_area",
        2: "footprint",
        3: "change_detection",
    }

    test_dir = os.path.abspath(__file__)
    sample_data_dir = os.path.join(test_dir, "/sample_data/")
    sample_file_name = project_types[project_type] + "_drafts.json"
    sample_file_path = os.path.join(sample_data_dir, sample_file_name)

    with open(sample_file_path) as sample_project_drafts_file:
        sample_project_drafts = json.load(sample_project_drafts_file)
    return sample_project_drafts


def create_project_draft(project_type: int = 0) -> list:
    """Create a sample project drafts in Firebase and return project ids."""
    project_draft_ids = []
    project_drafts = load_sample_project_drafts(project_type)

    fb_db = auth.firebaseDB()
    ref = fb_db.reference(f"/v2/projectDrafts/")

    for key, project_draft in project_drafts.items():
        project_draft_ids.append(ref.push(project_draft))

    return project_draft_ids
