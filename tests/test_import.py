import os
import pickle
from mapswipe_workers.basic import BaseFunctions


def import_process():
    firebase, postgres = BaseFunctions.get_environment('development')
    fb_db = firebase.database()

    imported_projects = BaseFunctions.run_import('development')

    # save all keys to disk
    filename = 'firebase_imported_projects.pickle'
    if os.path.isfile(filename):
        with open(filename, 'rb') as f:
            already_imported_projects = pickle.load(f)
        imported_projects = imported_projects + already_imported_projects

    with open(filename, 'wb') as f:
        pickle.dump(imported_projects, f)


if __name__ == '__main__':
    import_process()
    print("Everything passed")
