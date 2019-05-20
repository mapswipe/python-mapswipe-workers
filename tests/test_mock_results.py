import random
import pickle
import time

from mapswipe_workers import auth


def mock_user_contributions(
        fb_db,
        project_id,
        user_id,
        ):

    ref = fb_db.reference(f'groups/{project_id}/')
    groups = ref.order_by_key().limit_to_last(5).get()

    # finishedCounts = dict()
    # requiredCounts = dict()
    results = dict()
    results['results'] = dict()
    results['timestamp'] = time.time()

    for group_id, group in groups.items():
        # finishedCounts[group_id] = fb_db.reference(
        #         f'groups/{project_id}/{group_id}/finishedCount'
        #         ).get()
        # requiredCounts[group_id] = fb_db.reference(
        #        f'groups/{project_id}/{group_id}/requiredCount'
        #         ).get()
        tasks_ref = fb_db.reference(f'tasks/{project_id}/{group_id}/')
        tasks = tasks_ref.get()
        for task in tasks:
            results['results'][task['taskId']] = random.randint(1, 3)

        results_ref = fb_db.reference(
                f'results/{project_id}/{group_id}/{user_id}/'
                )

        results_ref.update(results)
        print(f'Uploaded results for group: {group_id}')

#     time.sleep(5)

#     for group_id, group in groups.items():
#         finishedCount = fb_db.reference(
#                 f'groups/{project_id}/{group_id}/finishedCount'
#                 ).get()
#         requiredCount = fb_db.reference(
#                f'groups/{project_id}/{group_id}/requiredCount'
#                 ).get()
#         assert finishedCounts[group_id] + 1 == finishedCount
#         assert requiredCounts[group_id] - 1 == requiredCount


if __name__ == '__main__':
    fb_db = auth.firebaseDB()

    filename = 'project_ids.pickle'
    with open(filename, 'rb') as f:
        project_ids = pickle.load(f)

    filename = 'user_ids.pickle'
    with open(filename, 'rb') as f:
        user_id = pickle.load(f)

    for project_id in project_ids:
        print('')
        print(
                f'start generating results for project ({project_id}) '
                f'and user ({user_id})'
                )
        mock_user_contributions(fb_db, project_id, user_id)

    print('Uploaded sample results to Firebase')
