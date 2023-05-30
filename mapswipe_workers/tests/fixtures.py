import json
import os

from tests.integration.set_up import upload_file_to_firebase

TEST_DIR = os.path.dirname(os.path.abspath(__file__))
FIXTURE_DIR = os.path.join(TEST_DIR, "fixtures")


def get_fixture(path):
    file_path = os.path.join(FIXTURE_DIR, path)
    with open(file_path) as file:
        return json.load(file)


def create_test_draft(
    fixture_path: str,
    fixture_name: str = "user",
    identifier: str = "",
    draftType: str = "projectDrafts",
) -> str:
    """
    Create test project drafts in Firebase and return project ids.
    Project drafts in Firebase are created by project manager using the dashboard.
    """
    if not identifier:
        identifier = f"test_{fixture_name}"
    upload_file_to_firebase(fixture_path, draftType, fixture_name)
    return identifier
