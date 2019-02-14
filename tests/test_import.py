import os
import pickle
from mapswipe_workers.basic import BaseFunctions


def import_process():
    firebase, postgres = BaseFunctions.get_environment('production')
    fb_db = firebase.database()

    imported_project_keys = BaseFunctions.run_import('production')

    # save all keys to disk
    filename = 'firebase_imported_project_keys.pickle'
    if os.path.isfile(filename):
        with open(filename, 'rb') as f:
            already_imported_project_keys = pickle.load(f)
        imported_project_keys = already_imported_project_keys + imported_project_keys

    with open(filename, 'wb') as f:
        pickle.dump(imported_project_keys, f)


if __name__ == '__main__':
    import_process()
    print("Everything passed")
