import os
import pickle

from mapswipe_workers.firebase_to_postgres import transfer_results
from mapswipe_workers.firebase_to_postgres import update_data


def load_project_ids_from_disk():
    filename = "project_ids.pickle"
    if os.path.isfile(filename):
        with open(filename, "rb") as f:
            existing_project_ids = pickle.load(f)
    else:
        existing_project_ids = set([])

    return existing_project_ids


def load_user_ids_from_disk():
    filename = "users.pickle"
    if os.path.isfile(filename):
        with open(filename, "rb") as f:
            users = pickle.load(f)
            user_ids = list(users.keys())
    else:
        user_ids = set([])

    return user_ids


if __name__ == "__main__":
    # only perform transfer for specified project ids
    project_ids = load_project_ids_from_disk()
    user_ids = load_user_ids_from_disk()

    update_data.update_user_data(user_ids)
    update_data.update_project_data(project_ids)
    transfer_results.transfer_results(project_id_list=project_ids)
