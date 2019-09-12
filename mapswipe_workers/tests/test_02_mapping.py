import os
import random
import string
import pickle
import datetime

from mapswipe_workers.utils import user_management
from mapswipe_workers.auth import firebaseDB


def do_mapping(uid, user, project_id):
    # TODO: use shallow for groups and tasks to reduce data transfer
    print(f'user {uid} do some mapping for {project_id}')

    # sign in user through REST api
    normal_user = user_management.sign_in_with_email_and_password(user['email'], user['password'])

    # get 3 groups to work on using firebase REST api
    path = f'/v2/groups/{project_id}'
    custom_arguments = 'orderBy="requiredCount"&limitToLast=3&'  # make sure to set & at the end of the string
    groups = user_management.get_firebase_db(path, custom_arguments, normal_user['idToken'])

    for group_id, group in groups.items():
        start_time = datetime.datetime.utcnow().isoformat()[0:-3]+'Z'
        path = f'/v2/tasks/{project_id}/{group_id}'
        custom_arguments = ''
        tasks = user_management.get_firebase_db(path, custom_arguments, normal_user['idToken'])

        results = {}
        for task in tasks:
            task_id = task['taskId']
            results[task_id] = random.randint(0, 3)

        end_time = datetime.datetime.utcnow().isoformat()[0:-3]+'Z'
        path = f'/v2/results/{project_id}/{group_id}/{uid}'
        data = {
            'results': results,
            'timestamp': end_time,
            'startTime': start_time,
            'endTime': end_time
        }
        user_management.set_firebase_db(path, data, normal_user['idToken'])


def get_firebase_data(project_ids, users, filename):
    fb_db = firebaseDB()

    firebase_data = {
        'projects': {},
        'groups': {},
        'results': {},
        'users': {}
    }

    for project_id in project_ids:
        project_ref = fb_db.reference(f'v2/proejcts/{project_id}/')
        firebase_data['projects'][project_id] = project_ref.get()

        groups_ref = fb_db.reference(f'v2/groups/{project_id}/')
        firebase_data['groups'][project_id] = groups_ref.get()

        results_ref = fb_db.reference(f'v2/results/{project_id}/')
        firebase_data['results'][project_id] = results_ref.get()

    for uid, user in users.items():
        user_ref = fb_db.reference(f'v2/users/{uid}/')
        firebase_data['users'][uid] = user_ref.get()

    with open(filename, 'wb') as f:
        pickle.dump(firebase_data, f)

    return firebase_data


def create_normal_users():
    users = {}

    for i in range(0,3):
        random_string = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        email = f'test_{random_string}@mapswipe.org'
        username = f'test_{random_string}'
        password = 'mapswipe'

        # create normal user
        user = user_management.create_user(email, username, password)
        users[user.uid] = {
            'email': email,
            'username': username,
            'password': password
        }

    return users


def load_project_ids_from_disk():
    filename = 'project_ids.pickle'
    if os.path.isfile(filename):
        with open(filename, 'rb') as f:
            existing_project_ids = pickle.load(f)
    else:
        existing_project_ids = set([])

    return existing_project_ids


def save_users_to_disk(users):
    filename = 'users.pickle'
    if os.path.isfile(filename):
        with open(filename, 'rb') as f:
            existing_users = pickle.load(f)
    else:
        existing_users = {}

    for uid, user in users.items():
        existing_users[uid] = user

    with open(filename, 'wb') as f:
        pickle.dump(existing_users, f)


if __name__ == '__main__':
    try:
        # create some test users
        users = create_normal_users()
        save_users_to_disk(users)

        # get project ids
        project_ids = load_project_ids_from_disk()

        # get firebase projects, groups and results before mapping
        filename_before = 'firebase_data_before.pickle'
        firebase_data_before = get_firebase_data(project_ids, users, filename_before)

        # generate some results each user and project
        for uid, user in users.items():
            for project_id in project_ids:
                do_mapping(uid, user, project_id)

        # get firebase projects, groups and results before mapping
        filename_after = 'firebase_data_after.pickle'
        firebase_data_after = get_firebase_data(project_ids, users, filename_after)

        # TODO: compare firebase before and after data
        # TODO: test project results counter progress
        # TODO: test group results counter progress
        # TODO: test user stats progress

    except Exception:
        # TODO: do clean up properly

        for uid, user in users.items():
            user_management.delete_user(user['email'])
        raise Exception