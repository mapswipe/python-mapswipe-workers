import random
import datetime
import pickle

from mapswipe_workers import auth


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
    else:
        ref.update({
            "timestamp": timestamp,
            "resultCount": result.get('resultCount', 0) + 1,
            task_id: {
                "result": rn
                }
            })
    print("uploaded result")

    ref = fb_db.reference(
            f'users/{user_id}'
            )
    user = ref.get()

    if 'contributions' in user:
        if project_id not in user['contributions']:
            ref_project = fb_db.reference(
                    f'projects/{project_id}/contributors'
                    )
            contributors = ref_project.get() + 1
            ref_project.update(contributors)

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

    ref = fb_db.reference(f'groups/{project_id}')
    group = ref.get()
    ref.update({
        'completedCount': group['completedCount'] + 1
        })
    print("updated project completed count")


def mock_user_contributions(
        fb_db,
        project_id,
        user_id,
        ):

    # temporary workaround because of faulty string encoding

    ref = fb_db.reference(f'groups/{project_id}/')
    groups = ref.order_by_child('completedCount').limit_to_last(5).get()

    for group_id, group in groups.items():
        ref = fb_db.reference(f'tasks/{project_id}/{group_id}/')
        tasks = ref.get()

        numberOfTasks = group['numberOfTasks']
        random_sample = random.sample(tasks, int(numberOfTasks/2))
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

    for project_id in project_ids:
        mock_user_contributions(fb_db, project_id, user_id)
