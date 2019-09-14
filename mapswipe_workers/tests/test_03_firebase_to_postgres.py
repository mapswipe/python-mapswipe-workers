import os
import pickle

from mapswipe_workers.firebase_to_postgres import transfer_results
from mapswipe_workers.firebase_to_postgres import update_data


def load_project_ids_from_disk():
    filename = 'project_ids.pickle'
    if os.path.isfile(filename):
        with open(filename, 'rb') as f:
            existing_project_ids = pickle.load(f)
    else:
        existing_project_ids = set([])

    return existing_project_ids

if __name__ == '__main__':

    project_ids = load_project_ids_from_disk()

    # TODO: review copy users, we often get: "results_temp" violates foreign key constraint "results_temp_user_id_fkey"
    update_data.copy_new_users()
    transfer_results.transfer_results(project_id_list=project_ids)
