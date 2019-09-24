import pickle
import os

from mapswipe_workers import auth
from mapswipe_workers.definitions import DATA_PATH


def delete_sample_data_from_firebase(fb_db, project_id):
    ref = fb_db.reference(f'v2/results/{project_id}')
    ref.set({})
    ref = fb_db.reference(f'v2/tasks/{project_id}')
    ref.set({})
    ref = fb_db.reference(f'v2/groups/{project_id}')
    ref.set({})
    ref = fb_db.reference(f'v2/projects/{project_id}')
    ref.set({})
    ref = fb_db.reference(f'v2/projectDrafts/{project_id}')
    ref.set({})
    print(
            f'Firebase: '
            f'deleted projectDraft, project, groups, tasks and results '
            f'with the project id: {project_id}'
            )


def delete_sample_results_from_postgres(pg_db, project_id):
    p_con = pg_db()
    sql_query = '''
        DELETE FROM results
        WHERE EXISTS (
            SELECT project_id
            FROM results
            WHERE project_id = %s
            );
        DELETE FROM tasks WHERE project_id = %s;
        DELETE FROM groups WHERE project_id = %s;
        DELETE FROM projects WHERE project_id = %s;
        '''

    data = [
        project_id,
        project_id,
        project_id,
        project_id,
    ]

    p_con.query(sql_query, data)
    print(
            f'Postgres: '
            f'deleted project, groups, tasks and results '
            f'with the project id: {project_id}'
            )


def delete_local_files(project_id):
    fn = f'{DATA_PATH}/results/results_{project_id}.json'
    if os.path.isfile(fn):
        os.remove(fn)
    # os.remove(
    #         f'{DATA_PATH}'
    #         f'/progress/progress_{project_id}.json'
    #         )
    # os.remove(
    #         f'{DATA_PATH}'
    #         f'/progress/progress_{project_id}.json'
    #         )
    fn = f'{DATA_PATH}/input_geometries/raw_input_{project_id}.geojson'
    if os.path.isfile(fn):
        os.remove(fn)
    fn = f'{DATA_PATH}/input_geometries/valid_input_{project_id}.geojson'
    if os.path.isfile(fn):
        os.remove(fn)
    print(
            f'Local files: '
            f'deleted raw_input and valid_input files'
            f'with the project id: {project_id}'
            )


def delete_sample_users(fb_db):
    pass


if __name__ == '__main__':
    pg_db = auth.postgresDB
    fb_db = auth.firebaseDB()

    filename = 'project_ids.pickle'

    if os.path.isfile(filename):
        with open(filename, 'rb') as f:
            project_ids = pickle.load(f)
        for project_id in project_ids:
            delete_sample_data_from_firebase(fb_db, project_id)
            delete_sample_results_from_postgres(pg_db, project_id)
            delete_local_files(project_id)
        os.remove('project_ids.pickle')
    else:
        print('No project_ids.pickle file found')

    # TODO: Delete users from postgres
    filename = 'user_ids.pickle'
    if os.path.isfile(filename):
        with open(filename, 'rb') as f:
            user_ids = pickle.load(f)
        for user_id in user_ids:
            ref = fb_db.reference(f'v2/users/{user_id}')
            ref.set({})
            print(f'Firebase: deleted user with the user id: {user_id}')
        os.remove('user_ids.pickle')
    else:
        print('No user_ids.pickle file found')

    print('Deleted all sample data in Firebase, Postgres and on disk')
