import os
import random
import string
import pickle
import datetime
import time
from tabulate import tabulate

from mapswipe_workers.utils import user_management
from mapswipe_workers.auth import firebaseDB


def do_mapping(uid, user, project_id, number_of_groups):
    # TODO: use shallow for groups and tasks to reduce data transfer
    print(f'user {uid} do some mapping for {project_id}')

    # sign in user through REST api
    normal_user = user_management.sign_in_with_email_and_password(user['email'], user['password'])

    # get 3 groups to work on using firebase REST api
    path = f'/v2/groups/{project_id}'
    custom_arguments = f'orderBy="requiredCount"&limitToLast={number_of_groups}&'  # make sure to set & at the end of the string
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


def get_firebase_data(project_ids, uid, filename):
    fb_db = firebaseDB()

    firebase_data = {
        'projects': {},
        'groups': {},
        'results': {},
        'users': {}
    }

    for project_id in project_ids:
        project_ref = fb_db.reference(f'v2/projects/{project_id}/')
        firebase_data['projects'][project_id] = project_ref.get()

        groups_ref = fb_db.reference(f'v2/groups/{project_id}/')
        raw_groups = groups_ref.get()
        # due to firebase reasons sometimes we get an array with many "None" instead of an dict
        # we need to make sure to create a proper dict here
        if isinstance(raw_groups, dict):
            firebase_data['groups'][project_id] = raw_groups
        else:
            firebase_data['groups'][project_id] = {}
            for group in raw_groups:
                if group:
                    group_id = str(group['groupId'])
                    firebase_data['groups'][project_id][group_id] = group

        results_ref = fb_db.reference(f'v2/results/{project_id}/')
        firebase_data['results'][project_id] = results_ref.get()

    user_ref = fb_db.reference(f'v2/users/{uid}/')
    firebase_data['users'][uid] = user_ref.get()

    with open(filename, 'wb') as f:
        pickle.dump(firebase_data, f)

    return firebase_data


def create_normal_users(number_of_users):
    users = {}

    for i in range(0,number_of_users):
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


def test_firebase_functions_users(firebase_data_before, firebase_data_after):
    # TODO: check 'contributions' attribute for user


    for user_id in firebase_data_after['users'].keys():

        results_task_count = 0
        results_group_count = 0
        results_project_count = 0
        results_group_ids = set([])
        results_project_ids = set([])

        # get user level counters
        user_task_contribution_count_before = firebase_data_before['users'].get(user_id, {}).get(
            'taskContributionCount', 0)
        user_task_contribution_count_after = firebase_data_after['users'][user_id]['taskContributionCount']

        user_group_contribution_count_before = firebase_data_before['users'].get(user_id, {}).get(
            'groupContributionCount', 0)
        user_group_contribution_count_after = firebase_data_after['users'][user_id]['groupContributionCount']

        user_project_contribution_count_before = firebase_data_before['users'].get(user_id, {}).get(
            'projectContributionCount', 0)
        user_project_contribution_count_after = firebase_data_after['users'][user_id]['projectContributionCount']

        for project_id in firebase_data_before['projects'].keys():
            for group_id in firebase_data_after['results'][project_id].keys():
                if user_id in firebase_data_after['results'][project_id][group_id].keys():
                    if not firebase_data_before['results'].get(project_id, {}).get(group_id, {}).get(user_id, {}).get('results',
                                                                                                           None):
                        results_project_ids.add(project_id)
                        results_group_ids.add(f'{project_id}_{group_id}')
                        results_task_count += len(firebase_data_after['results'][project_id][group_id][user_id]['results'])
                        results_group_count = len(results_group_ids)
                        results_project_count = len(results_project_ids)

        # check user level values
        table = [
            ['result project count', '-', results_project_count],
            ['result group count', '-', results_group_count],
            ['result task count', '-', results_task_count],
            ['project contribution count', user_project_contribution_count_before,
             user_project_contribution_count_after],
            ['group contribution count', user_group_contribution_count_before,
             user_group_contribution_count_after],
            ['task contribution count', user_task_contribution_count_before,
             user_task_contribution_count_after]
        ]
        print(tabulate(table, headers=[user_id, 'before', 'after']))

        assert user_project_contribution_count_after == user_project_contribution_count_before + results_project_count, \
            f'project contribution count not correct for user: {user_id}'

        assert user_group_contribution_count_after == user_group_contribution_count_before + results_group_count, \
            f'group contribution count not correct for user: {user_id}'

        assert user_task_contribution_count_after == user_task_contribution_count_before + results_task_count, \
            f'task contribution count not correct for user: {user_id}'



def test_firebase_functions_results(
        firebase_data_before,
        firebase_data_after
        ):
    '''
    Test result count and progress of project
    when new results are written to the firebase.
    '''

    for project_id in firebase_data_before['projects'].keys():

        total_result_count = 0 # refers to all results uploaded by users
        true_result_count = 0  # refers to all results that actually increase progress
        group_result_count = 0 # refers to all results that actually increase progress

        # get project level result count and progress
        project_result_count_before = firebase_data_before['projects'][project_id].get('resultCount', 0)
        project_result_count_after = firebase_data_after['projects'][project_id]['resultCount']

        project_progress_before = firebase_data_before['projects'][project_id].get('progress', 0)
        project_progress_after = firebase_data_after['projects'][project_id]['progress']

        project_required_results_before = firebase_data_before['projects'][project_id]['numberOfTasks']
        project_required_results_after = firebase_data_after['projects'][project_id]['numberOfTasks']

        project_contributor_count_before = firebase_data_before['projects'][project_id].get('contributorCount', 0)
        project_contributor_count_after = firebase_data_after['projects'][project_id]['contributorCount']


        # go through all results and check counts for groups
        for group_id in firebase_data_after['results'][project_id].keys():
            for user_id in firebase_data_after['results'][project_id][group_id].keys():

                # check if results have been uploaded already before
                if not firebase_data_before['results'].get(project_id, {}).get(group_id, {}).get(user_id, {}).get('results', None):
                    user_result_count = len(firebase_data_after['results'][project_id][group_id][user_id]['results'])
                    total_result_count += user_result_count

                    if firebase_data_after['groups'][project_id][group_id]['requiredCount'] >= 0:
                        group_result_count += firebase_data_after['groups'][project_id][group_id]['numberOfTasks']
                        true_result_count += user_result_count

                        group_finished_count_before = firebase_data_before['groups'][project_id][group_id][
                            'finishedCount']
                        group_required_count_before = firebase_data_before['groups'][project_id][group_id][
                            'requiredCount']
                        group_progress_before = firebase_data_before['groups'][project_id][group_id][
                            'progress']

                        group_finished_count_after = firebase_data_after['groups'][project_id][group_id][
                            'finishedCount']
                        group_required_count_after = firebase_data_after['groups'][project_id][group_id][
                            'requiredCount']
                        group_progress_after = firebase_data_after['groups'][project_id][group_id][
                            'progress']

                        table = [
                            ['group finished count', group_finished_count_before, group_finished_count_after],
                            ['group required count', group_required_count_before, group_required_count_after],
                            ['group progress', group_progress_before, group_progress_after]
                        ]

                        print(tabulate(table, headers=[group_id, 'before', 'after']))

                        # check finished count, required count and progress on group level
                        assert group_finished_count_after == group_finished_count_before + 1, \
                            f'group finished count not correct for project {project_id}, group {group_id}'

                        assert group_required_count_after == group_required_count_before - 1, \
                            f'group finished count not correct for project {project_id}, group {group_id}'

                        assert group_progress_after <= 100, \
                            f'progress bigger than 100% for project Id: {project_id}, group {group_id}'

                        if group_required_count_after > 0:
                            assert group_progress_after == round(
                                100 * float(group_finished_count_after) / (float(group_finished_count_after +  group_required_count_after))), \
                                f'wrong progress for project Id: {project_id}, group {group_id}'
                        else:
                            assert group_progress_after == 100, \
                                f'progress must be 100 if required count is negative or zero \ ' \
                                f'for project Id: {project_id}, group {group_id}'


        # check project level values
        table = [
            ['uploaded results', '-', total_result_count],
            ['true results', '-', true_result_count],
            ['group results count', '-', group_result_count],
            ['project result count', project_result_count_before, project_result_count_after],
            ['project required results', project_required_results_before, project_required_results_after],
            ['project progress', project_progress_before, project_progress_after],
            ['project contributor count', project_contributor_count_before, project_contributor_count_after]
        ]
        print(tabulate(table, headers=[project_id, 'before', 'after']))

        assert group_result_count == true_result_count, \
            f'group result count and true result count not matching for project Id: {project_id}'

        assert group_result_count == (project_result_count_after - project_result_count_before), \
            f'wrong result count for project Id: {project_id}'

        # TODO: double check this functions and how it's done in firebase functions
        assert project_progress_after == round(100 * float(project_result_count_after) / float(project_required_results_after)), \
            f'wrong progress for project Id: {project_id}'

        assert project_progress_after <= 100, \
            f'progress bigger than 100% for project Id: {project_id}'

        if not firebase_data_before['users'].get(user_id, {}).get(project_id, {}).get('contributions', None):
            assert project_contributor_count_after == project_contributor_count_before + 1
        else:
            assert project_contributor_count_after == project_contributor_count_before


if __name__ == '__main__':

    number_of_users = 1
    number_of_groups = 2  # now many groups should be mapped per user and project

    # create some test users
    users = create_normal_users(number_of_users)
    save_users_to_disk(users)


    # get project ids
    project_ids = load_project_ids_from_disk()

    # generate some results each user and project
    for uid, user in users.items():

        # get firebase projects, groups and results before mapping
        filename_before = 'firebase_data_before.pickle'
        firebase_data_before = get_firebase_data(project_ids, uid, filename_before)

        for project_id in project_ids:
            do_mapping(uid, user, project_id, number_of_groups)

        # wait 3s seconds and get firebase projects, groups and results after mapping
        time.sleep(3)
        filename_after = 'firebase_data_after.pickle'
        firebase_data_after = get_firebase_data(project_ids, uid, filename_after)

        test_firebase_functions_results(firebase_data_before, firebase_data_after)
        test_firebase_functions_users(firebase_data_before, firebase_data_after)

    # TODO: do clean up properly


