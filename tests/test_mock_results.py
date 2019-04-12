import random
from datetime import datetime
import pickle

from mapswipe_workers import auth
from mapswipe_workers.definitions import logger


def create_result(
        fb_db,
        project_id,
        group_id,
        user_id,
        task_id,
        ):

    result_ref = fb_db.reference(
            f'results/{project_id}/{group_id}/{user_id}'
            )
    result = result_ref.get()

    rn = random.randint(1, 3)
    # timestamp = datetime.now().timestamp()

    if result is None:
        result_data = {
            task_id: rn
            }
        result_ref.set(result_data)
    else:
        result_ref.update({
            task_id: rn
            })
    print(f'uploaded result for task: {task_id}')

    def increment(current_value):
        return current_value + 1 if current_value else 1

    # user_ref = fb_db.reference(f'users/{user_id}')
    # user = user_ref.get()
    # project_contributors_ref = fb_db.reference(
    #         f'projects/{project_id}/contributors'
    #         )

    # if 'contributions' in user:
    #     if project_id not in user['contributions']:
    #         project_contributors_ref.transaction(increment)
    #         print('incremented project contributors by one')

    # user_data = {
    #         "contributionCount": user['contributionCount'] + 1,
    #         "distance": user['distance'] + 12,
    #         "contributions": {
    #             project_id: {
    #                 group_id: timestamp
    #                 }
    #             }
    #         }
    # user_ref.update(user_data)
    # print("updated user contribution count and contributions")

    # group_ref = fb_db.reference(
    #         f'groups/{project_id}/{group_id}/completedCount'
    #         )
    # group_ref.transaction(increment)
    # print("incremeted project completed count by one")


def mock_user_contributions(
        fb_db,
        project_id,
        user_id,
        ):

    ref = fb_db.reference(f'groups/{project_id}/')
    groups = ref.order_by_key().limit_to_last(5).get()

    for group_id, group in groups.items():
        ref = fb_db.reference(f'tasks/{project_id}/{group_id}/')
        tasks = ref.get()

        numberOfTasks = group['numberOfTasks']
        random_sample = random.sample(tasks, int(numberOfTasks/5))
        print(
                f'Generate results for a random selection selection of '
                f'{len(random_sample)} tasks'
                )
        for task in random_sample:
            create_result(
                    fb_db,
                    project_id,
                    group_id,
                    user_id,
                    task['taskId'],
                    )


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
