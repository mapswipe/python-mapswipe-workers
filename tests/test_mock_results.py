import random
import datetime
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

    ref = fb_db.reference(
            f'results/{project_id}/{group_id}/{user_id}'
            )
    result = ref.get()

    rn = random.randint(1, 3)
    timestamp = datetime.datetime.utcnow().strftime('%m/%d/%Y')

    if result is None:
        result_data = {
            "timestamp": timestamp,
            "resultCount": 1,
            task_id: {
                "result": rn
                }
            }
        ref.set(result_data)
    else:
        ref.update({
            "timestamp": timestamp,
            "resultCount": result.get('resultCount', 0) + 1,
            task_id: {
                "result": rn
                }
            })
    print("uploaded result")

    def increment(current_value):
        return current_value + 1 if current_value else 1

    user_ref = fb_db.reference(f'users/{user_id}')
    user_contributions_ref = fb_db.reference(f'users/{user_id}/contributions')
    project_contributors_ref = fb_db.reference(f'projects/{project_id}/contributors')
    user = ref.get()

    if 'contributions' in user:
        if project_id not in user['contributions']:
            project_contributors_ref.transaction(increment)

    user_data = {
            "contributedCount": user['contributedCount'] + 1,
            "distance": user['distance'] + 12,
            "username": user['username'],
            "contributions": {
                project_id: {
                    group_id: timestamp
                    }
                }
            }
    ref.update(user_data)
    print("updated user contribution count and contributions")

    group_ref = fb_db.reference(f'groups/{project_id}/{group_id}/completedCount')
    group_ref.transaction(increment)
    print("updated project completed count")


def mock_user_contributions(
        fb_db,
        project_id,
        user_id,
        ):

    ref = fb_db.reference(f'groups/{project_id}/')
    groups = ref.order_by_child('completedCount').limit_to_last(5).get()

    for group_id, group in groups.items():
        ref = fb_db.reference(f'tasks/{project_id}/{group_id}/')
        tasks = ref.get()

        numberOfTasks = group['numberOfTasks']
        random_sample = random.sample(tasks, int(numberOfTasks/10))
        print(f'random sample has size: {random_sample.len()}')
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

    logger.info('test')

    filename = 'project_ids.pickle'
    with open(filename, 'rb') as f:
        project_ids = pickle.load(f)

    filename = 'user_ids.pickle'
    with open(filename, 'rb') as f:
        user_id = pickle.load(f)

    for project_id in project_ids:
        mock_user_contributions(fb_db, project_id, user_id)
