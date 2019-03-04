import pickle
from mapswipe_workers.basic import BaseFunctions


def test_transfer_results():

    filename = 'firebase_imported_projects.pickle'
    with open(filename, 'rb') as f:
        imported_projects = pickle.load(f)

    project_ids = [i[1] for i in imported_projects]
    BaseFunctions.run_export('development', project_ids)


if __name__ == '__main__':
    test_transfer_results()
