import os
import pickle

from mapswipe_workers.basic import BaseFunctions


def test_import_process():
    imported_projects = BaseFunctions.run_import('production')

    # save all keys to disk
    filename = 'imported_project_ids.pickle'
    if os.path.isfile(filename):
        with open(filename, 'rb') as f:
            already_imported_project_ids = pickle.load(f)
        imported_project_ids = imported_project_ids + already_imported_project_ids

    with open(filename, 'wb') as f:
        pickle.dump(imported_project_ids, f)


if __name__ == '__main__':
    test_import_process()
    print("Everything passed")
