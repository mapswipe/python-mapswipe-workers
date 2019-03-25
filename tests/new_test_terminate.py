import pickle
import os

from mapswipe_workers.basic import auth
from mapswipe_workers.basic import BaseFunctions
from mapswipe_workers.definitions import DATA_PATH


def delete_sample_data_from_firebase(fb_db, project_id):

    ref = fb_db.reference(f'groups/{project_id}')
    ref.set({})
    ref = fb_db.reference('tasks/{project_id}')
    ref.set({})
    ref = fb_db.reference('results/{project_id}')
    ref.set({})
    ref = fb_db.reference('projects/{project_id}')
    ref.set({})
    ref = fb_db.reference('projectDrafts/{project_id}')
    ref.set({})

    print(
            f'deleted projectDraft, project, groups, tasks and results'
            f'in firebase for the project with the id: {project_id}'
            )


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


def delete_sample_users(fb_db):
    pass

if __name__ == '__main__':
    #pg_db = auth.postgresDB()
    fb_db = auth.firebaseDB()

    filename = 'project_ids.pickle'
    if os.path.isfile(filename):
        with open(filename, 'rb') as f:
            project_ids = pickle.load(f)
        for project_id in project_ids:
            delete_sample_data_from_firebase(fb_db, project_id)
            # delete_sample_results_from_postgres(pg_db, project_id)
        os.remove('project_ids.pickle')


    filename = 'user_ids.pickle'
    if os.path.isfile(filename):
        with open(filename, 'rb') as f:
            user_ids = pickle.load(f)
        for user_id in user_ids:
            ref = fb_db.reference(f'users/{user_ids}')
            ref.set({})
        os.remove('user_ids.pickle')

    # delete_local_files(project_id, import_key)

    # os.remove('firebase_uploaded_projects.pickle')
    # print('deleted firebase_imported_projects.pickle and firebase_uploaded_projects.pickle')
