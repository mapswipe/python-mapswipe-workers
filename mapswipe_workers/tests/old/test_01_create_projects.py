import os
import random
import string
import json
import glob
import pickle

from mapswipe_workers.utils import user_management
from mapswipe_workers import mapswipe_workers


def create_project_manager(email, username, password):
    user = user_management.create_user(email, username, password)
    user_management.set_project_manager_rights(email)
    return user


def load_sample_project_drafts():
    sample_data = {}
    test_dir = os.path.dirname(os.path.abspath(__file__))
    sample_data_dir = os.path.join(test_dir, "../sample_data/")
    for sample_project_drafts_json in glob.glob(sample_data_dir + "*_drafts.json"):
        if sample_project_drafts_json == "build_area_to_big_project_drafts_test.json":
            continue
        with open(sample_project_drafts_json) as f:
            sample_project_drafts = json.load(f)
            for key, sample_project_draft in sample_project_drafts.items():
                sample_data[key] = sample_project_draft

    return sample_data


def save_project_ids_to_disk(project_ids):
    filename = "project_ids.pickle"
    if os.path.isfile(filename):
        with open(filename, "rb") as f:
            existing_project_ids = set(pickle.load(f))
    else:
        existing_project_ids = set([])

    for project_id in project_ids:
        existing_project_ids.add(project_id)

    with open(filename, "wb") as f:
        pickle.dump(existing_project_ids, f)


def test_initialize_project_drafts(email, password):
    project_ids = set([])
    project_manager = user_management.sign_in_with_email_and_password(email, password)
    project_drafts = load_sample_project_drafts()

    for key, project_draft in project_drafts.items():
        # TODO: add some random characters to key and use this as a project_id instead
        project_ids.add(key)
        path = f"/v2/projectDrafts/{key}"  # make sure that path starts with '/'
        user_management.set_firebase_db(path, project_draft, project_manager["idToken"])

    return project_manager, project_ids


def test_change_project_status(project_ids, email, password):

    rest_user = user_management.sign_in_with_email_and_password(email, password)

    for project_id in project_ids:
        # set project status to active
        path = f"/v2/projects/{project_id}/status"
        data = "active"
        user_management.set_firebase_db(path, data, rest_user["idToken"])

        # set project status to inactive
        path = f"/v2/projects/{project_id}/status"
        data = "inactive"
        user_management.set_firebase_db(path, data, rest_user["idToken"])


if __name__ == "__main__":
    try:
        random_string = "".join(
            random.choices(string.ascii_uppercase + string.digits, k=8)
        )
        email = f"test_manager_{random_string}@mapswipe.org"
        username = f"test_manager_{random_string}"
        password = "mapswipe"

        # create 1 project manager
        user = create_project_manager(email, username, password)

        # initialize project drafts
        project_manager, project_ids = test_initialize_project_drafts(email, password)
        save_project_ids_to_disk(project_ids)

        # create projects
        mapswipe_workers._run_create_projects(project_ids)

        # activate/deactivate project as project manager
        test_change_project_status(project_ids, email, password)

        user_management.delete_user(email)

    except Exception:
        # TODO: do clean up properly
        for key in project_ids:
            path = f"/v2/projectDrafts/"  # make sure that path starts with '/'
            data = {key: None}
            user_management.update_firebase_db(path, data, project_manager["idToken"])

        user_management.delete_user(email)
        raise Exception
