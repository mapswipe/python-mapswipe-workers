import random
import pickle
import json
import time


from mapswipe_workers import auth


def mock_user_contributions(
        fb_db,
        project_id,
        user_id,
        ):

    project_ref = fb_db.reference(f'projects/{project_id}/')
    project_data_before = project_ref.get()

    groups_ref = fb_db.reference(f'groups/{project_id}/')
    groups_data_before = groups_ref.order_by_key().limit_to_last(5).get()

    user_ref = fb_db.reference(f'users/{user_id}/')
    user_data_before = user_ref.get()

    results = dict()
    results['results'] = dict()
    results['timestamp'] = '2019-06-18T16:14:04.405Z'
    results['startTime'] = '2019-06-18T16:09:04.405Z'
    results['endTime'] = '2019-06-18T16:14:04.405Z'

    times = {
            'timestamp': results['timestamp'],
            'startTime': results['startTime'],
            'endTime': results['endTime']
            }

    for group_id, group in groups_data_before.items():
        tasks_ref = fb_db.reference(f'tasks/{project_id}/{group_id}/')
        tasks = tasks_ref.get()
        for task in tasks:
            results['results'][task['taskId']] = random.randint(1, 3)

        results_ref = fb_db.reference(
                f'results/{project_id}/{group_id}/{user_id}/'
                )

        results_ref.update(results)
        print(f'Uploaded results for group: {group_id}')

    return (project_data_before, groups_data_before, user_data_before, times)


def test_project_counter_progress(
        fb_db,
        project_id,
        groups_data_before,
        project_data_before,
        ):
    '''
    Test result count and progress of project
    when new results are written to the firebase.
    '''
    project_ref = fb_db.reference(f'projects/{project_id}/')
    project_data_after = project_ref.get()

    result_count = project_data_before['resultCount']

    for group_id, group in groups_data_before.items():
        if group['requiredCount'] <= 0:
            continue
        else:
            result_count += group['numberOfTasks']

    result_count_after = project_data_after['resultCount']
    number_of_tasks = project_data_after['numberOfTasks']
    progress_after = project_data_after['progress']
    contributor_count = project_data_after['contributorCount']
    assert result_count_after == result_count, \
        f'project Id: {project_id}'
    if project_data_before['progress'] != 100:
        assert progress_after == round(result_count_after*100/number_of_tasks), \
            f'project Id: {project_id}'
    assert progress_after > 100, \
        f'project Id: {project_id}'
    assert contributor_count == 1, \
        f'project Id: {project_id}'


def test_group_counter_progress(
        fb_db,
        project_id,
        groups_data_before
        ):

    ref = fb_db.reference(f'groups/{project_id}/')
    groups = ref.order_by_key().limit_to_last(5).get()

    for group_id, group_data_after in groups.items():
        finished_count_before = groups_data_before[group_id]['finishedCount']
        finished_count_after = group_data_after['finishedCount']
        required_count_before = groups_data_before[group_id]['requiredCount']
        required_count_after = group_data_after['requiredCount']
        progress_before = groups_data_before[group_id]['progress']
        progress_after = group_data_after['progress']

        assert finished_count_before + 1 == finished_count_after, \
            f'project Id: {project_id}'
        assert required_count_before - 1 == required_count_after, \
            f'project Id: {project_id}'
        assert progress_after <= 100
        if progress_before == 100:
            assert progress_after == progress_before, \
                f'project Id: {project_id}'
        else:
            progress = round(
                    finished_count_after/(
                        finished_count_after+required_count_after
                        )*100
                    )
            assert progress_after == progress, \
                f'project Id: {project_id}'

    # TODO: Test with group without explicit results -> only timestamp
    # Test performance -> upload many many results


def test_user_stats(
        fb_db,
        user_id,
        project_ids,
        user_data_before
        ):
    user_ref = fb_db.reference(f'users/{user_id}/')
    user_data_after = user_ref.get()

    # Init counter with values befor sending results
    total_number_of_projects = (
            user_data_before['projectContributionCount'] + len(project_ids)
            )
    total_number_of_groups = user_data_before['groupContributionCount']
    total_number_of_tasks = user_data_before['taskContributionCount']

    contributions = dict()

    # Calculate should-be values for each counter
    for project_id in project_ids:
        print(user_data_before)
        for key in user_data_before['contributions'].keys():
            if project_id == key:
                total_number_of_projects -= 1
        groups_ref = fb_db.reference(f'groups/{project_id}/')
        groups = groups_ref.order_by_key().limit_to_last(5).get()
        contributions_group = dict()
        for group_id, group in groups.items():
            total_number_of_tasks += group['numberOfTasks']
            total_number_of_groups += 1
            contributions_group[group_id] = {
                    'endTime': times['endTime'],
                    'startTime': times['startTime'],
                    'timestamp': times['timestamp'],
                    }
        contributions[project_id] = contributions_group

    # Construct json with all data of user
    # for comparision with json of firebase
    # TODO: calculate timeSpentMapping
    user_data = {
            "contributions": contributions,
            "groupContributionCount": total_number_of_groups,
            "projectContributionCount": total_number_of_projects,
            "taskContributionCount": total_number_of_tasks,
            "timeSpentMapping": user_data_after['timeSpentMapping'],
            "username": user_data_after['username']
            }

    user_data = json.dumps(user_data, sort_keys=True)
    user_data_after = json.dumps(user_data_after, sort_keys=True)
    assert user_data == user_data_after, \
        f'user Id: {user_id}'


if __name__ == '__main__':
    fb_db = auth.firebaseDB()

    filename = 'project_ids.pickle'
    with open(filename, 'rb') as f:
        project_ids = pickle.load(f)

    filename = 'user_ids.pickle'
    with open(filename, 'rb') as f:
        user_id = pickle.load(f)

    firebase_data_before = dict()

    for project_id in project_ids:
        print('')
        print(
                f'start generating results for project ({project_id}) '
                f'and user ({user_id})'
                )
        firebase_data_before[project_id] = mock_user_contributions(
                fb_db,
                project_id,
                user_id
                )

    print()
    print('Uploaded sample results to Firebase.')
    print(
            f'Sleep for a 60 seconds to wait till '
            f'Firebase Functions are finished.'
            )

    time.sleep(60)

    print()
    print('Running tests for Firebase Functions.')

    for project_id in project_ids:
        project_data_before, groups_data_before, user_data_before, times = \
                firebase_data_before[project_id]
        test_group_counter_progress(
                fb_db,
                project_id,
                groups_data_before,
                )
        test_project_counter_progress(
                fb_db,
                project_id,
                groups_data_before,
                project_data_before,
                )
        test_user_stats(
                fb_db,
                user_id,
                project_ids,
                user_data_before,
                times,
                )
    print()
    print(
            f'Firebase functions for inc/dec of counters and '
            f'progress calculation terminated with expected results'
            )

    print()
    print(
            f'Firebase functions for keeping track of user contributions '
            f'terminated with expected results'
            )

    print()
    print('Finished tests successful')
