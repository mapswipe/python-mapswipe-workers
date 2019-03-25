import random
import time
import pickle
import requests
import json

from mapswipe_workers.basic import BaseFunctions
from mapswipe_workers.basic import auth


def create_build_area_result_in_firebase(
        fb_db,
        project_id,
        group_id,
        user_id,
        task_id,
        ):
    # TODO: user1.resultCount++ & write new timestamp

    ref = fb_db.reference(
            f'results/{project_id}/{group_id}/{user_id}/{task_id}'
            )
    result_data = {
        "device": "test_device",
        "item": "test_item",
        "result": random.randint(0, 3),
    }

    ref = fb_db.reference(
            f'results/{project_id}/{group_id}/{user_id}/{task_id}'
            )
    ref.set(result_data)


def create_footprint_result_in_firebase(
        fb_db,
        project_id,
        group_id,
        user_id,
        task_id,
        ):
    # TODO: user1.resultCount++ & write new timestamp

    result_data = {
        "device": "test_device",
        "item": "test_item",
        "result": random.randint(1, 3),
    }

    ref = fb_db.reference(
            f'results/{project_id}/{group_id}/{user_id}/{task_id}'
            )
    ref.set(result_data)


def mock_user_contributions(
        fb_db,
        project_id,
        user_id='test_user',
        ):

    # temporary workaround because of faulty string encoding

    ref = fb_db.reference(f'projects/{project_id}/')
    project = ref.get()
    ref = fb_db.reference(f'groups/{project_id}/')
    groups = ref.order_by_child("completedCount").limit_to_first(5).get()

    for group_id, group in groups.items():
        ref = fb_db.reference(f'tasks/{project_id}/{group_id}/')
        tasks = ref.get()

        if project['projectType'] == 1:
            count = group['count']
            random_sample = random.sample(tasks.keys(), int(count/2))
            for task_id in random_sample:
                create_build_area_result_in_firebase(
                        fb_db,
                        project_id,
                        group_id,
                        user_id,
                        task_id,
                        )
            print("created build area results in firebase")
        elif project_type == 2:
            for task_id in tasks.keys():
                create_footprint_result_in_firebase(
                        fb_db,
                        project_id,
                        group_id,
                        user_id,
                        task_id,
                        )
            print("created footprint results in firebase")

        # update groups completed count
        ref = db.reference(f'groups/{project_id}')
        ref.update({
            'completedCount': group['completedCount'] + 1
            })
        print("updated completed count")

    # firebase_instance = 'dev-mapswipe'
    # groups_url = 'https://{firebase_instance}.firebaseio.com/groups/{project_id}.json?orderBy=%22completedCount%22&limitToFirst=5'.format(
    #     project_id=project_id,
    #     firebase_instance=firebase_instance
    # )

    # groups = json.loads(requests.get(groups_url).text)
    # for group_id in groups.keys():

    #     val = groups[group_id]
    #     tasks = val['tasks']
    #     task_ids = tasks.keys()

    #     if project_type == 1:
    #         count = val['count']
    #         random_sample = random.sample(task_ids, int(count / 2))
    #         for task_id in random_sample:
    #             create_build_area_result_in_firebase(
    #                 project_id,
    #                 task_id,
    #                 user_id,
    #                 firebase,
    #             )
    #         print("created build area results in firebase")
    #     elif project_type == 2:
    #         for task_id in task_ids:
    #             create_footprint_result_in_firebase(
    #                 project_id,
    #                 task_id,
    #                 user_id,
    #                 firebase,
    #             )
    #         print("created footprint results in firebase")

        # # update groups completed count
        # old_completed_count = fb_db.child("groups").child(project_id).child(group_id).child(
        #     "completedCount").get().val()
        # fb_db.child("groups").child(project_id).child(group_id).update({"completedCount": old_completed_count + 1})
        # print("updated completed count")


if __name__ == '__main__':
    fb_db = auth.firebaseDB()

    filename = 'created_project_ids.pickle'
    with open(filename, 'rb') as f:
        project_ids = pickle.load(f)

    # Generate mock results for first two of the imported projects
    # for import_key, project_id, project_type in imported_projects:
    #     simulate_user_contributions(project_id, project_type, modus)

    for project_id in project_ids:
        mock_user_contributions(fb_db, project_id)
