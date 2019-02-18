import pickle
from mapswipe_workers.basic import BaseFunctions


def test_update():

    filename = 'firebase_imported_projects.pickle'
    with open(filename, 'rb') as f:
        imported_projects = pickle.load(f)

    project_ids = [i[1] for i in imported_projects]
    BaseFunctions.run_update('development', project_ids)


if __name__ == '__main__':
    test_update()
