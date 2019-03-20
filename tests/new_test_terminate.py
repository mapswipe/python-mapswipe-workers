import pickle
import os

from mapswipe_workers.basic import auth
from mapswipe_workers.basic import BaseFunctions
from mapswipe_workers.definitions import DATA_PATH


def delete_sample_data_from_firebase(fb_db, project_id):

    ref = fb_db.reference(f'projectDrafts/{project_id}')
    ref.set({})
    ref = fb_db.reference(f'groups/{project_id}')
    ref.set({})
    ref = fb_db.reference('tasks/{project_id}')
    ref.set({})
    ref = fb_db.reference('results/{project_id}')
    ref.set({})
    ref = fb_db.reference('projects/{project_id}')
    ref.set({})

    print(f'deleted projectDraft, project, groups, tasks and results\
            in firebase for the project with the id: {project_id}')


def delete_sample_results_from_postgres(pg_db, project_id, import_key):
    p_con = postgres()

    sql_query = '''
        DELETE FROM projects WHERE project_id = %s;
        DELETE FROM results WHERE project_id = %s;
        DELETE FROM tasks WHERE project_id = %s;
        DELETE FROM groups WHERE project_id = %s;
        DELETE FROM imports WHERE import_id = %s;
        '''

    data = [
        project_id,
        project_id,
        project_id,
        project_id,
        import_key
    ]

    p_con.query(sql_query, data)
    print('deleted import, project, groups, tasks, results in postgres')


def delete_local_files(project_id, import_key):

    try:
        os.remove(DATA_PATH+'/results/results_{}.json'.format(project_id))
        os.remove(DATA_PATH+'/progress/progress_{}.json'.format(project_id))
        os.remove(DATA_PATH+'/progress/progress_{}.json'.format(project_id))
    except:
        pass

    try:
        os.remove(DATA_PATH+'/input_geometries/raw_input_{}.geojson'.format(import_key))
        os.remove(DATA_PATH+'/input_geometries/valid_input_{}.geojson'.format(import_key))
    except:
        os.remove(DATA_PATH + '/input_geometries/raw_input_{}.kml'.format(import_key))


if __name__ == '__main__':
    firebase, postgres = BaseFunctions.get_environment(modus)
    pg_db = postgresDB
    fb_db = firebaseDB

    filename = 'firebase_project_ids.pickle'
    with open(filename, 'rb') as f:
        project_ids = pickle.load(f)

    print(imported_projects)

    for project_id in projects_ids:
        delete_sample_data_from_firebase(fb_db, project_id)
        # delete_sample_results_from_postgres(postgres, project_id, import_key)
        # delete_local_files(project_id, import_key)

    os.remove('firebase_project_ids.pickle')
    # os.remove('firebase_uploaded_projects.pickle')
    # print('deleted firebase_imported_projects.pickle and firebase_uploaded_projects.pickle')

