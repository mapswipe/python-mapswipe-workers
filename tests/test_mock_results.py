import random
import time
import pickle
from mapswipe_workers.basic import BaseFunctions
import requests
import json

def create_build_area_result_in_firebase(
        project_id,
        task_id,
        user_id,
        firebase,
        ):
    fb_db = firebase.database()

    result_data = {
        "device": "test_device",
        "id": task_id,
        "projectId": project_id,
        "item": "test_item",
        "result": random.randint(0, 3),
        "timestamp": int(time.time()*1000),
        "user": user_id,
        "wkt": ""
    }

    fb_db.child("results").child(task_id).child(user_id).child("data").set(result_data)


def create_footprint_result_in_firebase(
        project_id,
        task_id,
        user_id,
        firebase,
        ):
    fb_db = firebase.database()

    result_data = {
        "device": "test_device",
        "id": task_id,
        "projectId": project_id,
        "item": "test_item",
        "result": random.randint(1, 3),
        "timestamp": int(time.time()*1000),
        "user": user_id,
        "wkt": ""
    }

    fb_db.child("results").child(task_id).child(user_id).child("data").set(result_data)


def simulate_user_contributions(
        project_id,
        project_type,
        modus,
        user_id='test_user',
        ):
    firebase, postgres = BaseFunctions.get_environment(modus)

    # get groups from firebase for this project
    fb_db = firebase.database()

    # temporary workaround because of faulty string encoding
    '''
    groups = fb_db.child("groups").child(project_id).order_by_child("completedCount").limit_to_first(5).get()
    for group in groups.each():
        group_id = group.key()
        val = group.val()

        tasks = val['tasks']
        task_ids = tasks.keys()

        if project_type == 1:
            count = val['count']
            random_sample = random.sample(task_ids, int(count/2))
            for task_id in random_sample:
                create_build_area_result_in_firebase(
                        project_id,
                        task_id,
                        user_id,
                        firebase,
                        )
            print("created build area results in firebase")
        elif project_type == 2:
            for task_id in task_ids:
                create_footprint_result_in_firebase(
                        project_id,
                        task_id,
                        user_id,
                        firebase,
                        )
            print("created footprint results in firebase")
            
        # update groups completed count
        old_completed_count = fb_db.child("groups").child(project_id).child(group_id).child("completedCount").get().val()
        fb_db.child("groups").child(project_id).child(group_id).update({"completedCount":old_completed_count+1})
        print("updated completed count")
    '''

    firebase_instance = 'dev-mapswipe'
    groups_url = 'https://{firebase_instance}.firebaseio.com/groups/{project_id}.json?orderBy=%22completedCount%22&limitToFirst=5'.format(
        project_id=project_id,
        firebase_instance=firebase_instance
    )

    groups = json.loads(requests.get(groups_url).text)
    for group_id in groups.keys():

        val = groups[group_id]
        tasks = val['tasks']
        task_ids = tasks.keys()

        if project_type == 1:
            count = val['count']
            random_sample = random.sample(task_ids, int(count / 2))
            for task_id in random_sample:
                create_build_area_result_in_firebase(
                    project_id,
                    task_id,
                    user_id,
                    firebase,
                )
            print("created build area results in firebase")
        elif project_type == 2:
            for task_id in task_ids:
                create_footprint_result_in_firebase(
                    project_id,
                    task_id,
                    user_id,
                    firebase,
                )
            print("created footprint results in firebase")

        # update groups completed count
        old_completed_count = fb_db.child("groups").child(project_id).child(group_id).child(
            "completedCount").get().val()
        fb_db.child("groups").child(project_id).child(group_id).update({"completedCount": old_completed_count + 1})
        print("updated completed count")



if __name__ == '__main__':
    modus = 'development'
    firebase, postgres = BaseFunctions.get_environment(modus)

    filename = 'firebase_imported_projects.pickle'
    with open(filename, 'rb') as f:
        imported_projects = pickle.load(f)

    # Generate mock results for first two of the imported projects
    for import_key, project_id, project_type in imported_projects:
        simulate_user_contributions(project_id, project_type, modus)

    '''
    project_id = imported_projects[0][1]
    project_type = imported_projects[0][2]
    

    project_id = imported_projects[1][1]
    project_type = imported_projects[1][2]
    simulate_user_contributions(project_id, project_type, modus)
    '''