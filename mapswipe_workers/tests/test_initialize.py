import datetime as dt
import glob
import json
import os
import pickle

from mapswipe_workers import auth


def create_project_drafts_in_firebase(sample_project_draft, fb_db):

    ref = fb_db.reference('v2/projectDrafts/')

    project_id = ref.push(sample_project_draft).key
    print(
            f'Uploaded a new sample project draft with the id: '
            f'{project_id} \n'
            )
    return project_id


def create_user(fb_db):
    ref = fb_db.reference('v2/users/')
    user = {
            'contributions': {},
            'created': dt.datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
            'groupContributionCount': 0,
            'projectContributionCount': 0,
            'taskContributionCount': 0,
            'timeSpentMapping': 0,
            'username': 'test_user'
            }
    user_id = ref.push(user).key
    print(f'Uploaded a sample user with the id: {user_id}\n')
    save_user_id(user_id)


def save_project_ids_to_disk(project_ids):
    filename = 'project_ids.pickle'
    if os.path.isfile(filename):
        with open(filename, 'rb') as f:
            existing_project_ids = pickle.load(f)
        project_ids = existing_project_ids + project_ids

    with open(filename, 'wb') as f:
        pickle.dump(project_ids, f)


def save_user_id(user_id):
    filename = 'user_ids.pickle'
    if os.path.isfile(filename):
        with open(filename, 'rb') as f:
            existing_user_ids = pickle.load(f)
        if isinstance(existing_user_ids, list):
            user_ids = existing_user_ids.append(user_id)
        else:
            user_ids = [existing_user_ids, user_id]
    else:
        user_ids = [user_id]

    with open(filename, 'wb') as f:
        pickle.dump(user_ids, f)


if __name__ == '__main__':
    fb_db = auth.firebaseDB()

    project_ids = list()

    test_dir = os.path.dirname(os.path.abspath(__file__))
    sample_data_dir = os.path.join(test_dir, 'sample_data/')
    for sample_project_drafts_json in glob.glob(
            sample_data_dir + '*_drafts.json'
            ):
        if sample_project_drafts_json == 'build_area_to_big_project_drafts_test.json':
            continue
        with open(sample_project_drafts_json) as f:
            sample_project_drafts = json.load(f)
            for key, sample_project_draft in sample_project_drafts.items():
                project_id = create_project_drafts_in_firebase(
                        sample_project_draft,
                        fb_db
                        )
                print(
                        f'created {sample_project_draft["name"]} '
                        f'with project id: {project_id}'
                        )
                project_ids.append(project_id)
    save_project_ids_to_disk(project_ids)
    create_user(fb_db)
    print(
            'Created sample project drafts and ' +
            'a sample user in the Firebase Realtime Database.'
            )
