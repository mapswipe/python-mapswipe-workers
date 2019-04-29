import random
import pickle

from mapswipe_workers import auth


def mock_user_contributions(
        fb_db,
        project_id,
        user_id,
        ):

    ref = fb_db.reference(f'groups/{project_id}/')
    groups = ref.order_by_key().limit_to_last(5).get()
    results = dict()

    for group_id, group in groups.items():
        tasks_ref = fb_db.reference(f'tasks/{project_id}/{group_id}/')
        tasks = tasks_ref.get()
        for task in tasks:
            results[task['taskId']] = random.randint(1, 3)

        results_ref = fb_db.reference(
                f'results/{project_id}/{group_id}/{user_id}/results/'
                )
        results_ref.update(results)
        print(f'Uploaded results for group: {group_id}')


if __name__ == '__main__':
    fb_db = auth.firebaseDB()

    filename = 'project_ids.pickle'
    with open(filename, 'rb') as f:
        project_ids = pickle.load(f)

    filename = 'user_ids.pickle'
    with open(filename, 'rb') as f:
        user_id = pickle.load(f)
        print(user_id)

    for project_id in project_ids:
        print('')
        print(
                f'start generating results for project ({project_id}) '
                f'and user ({user_id})'
                )
        mock_user_contributions(fb_db, project_id, user_id)

    print('Uploaded sample results to Firebase')
