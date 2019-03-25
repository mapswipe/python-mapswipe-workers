import os
import pickle
import json

from mapswipe_workers.basic import auth


def create_project_drafts_in_firebase(fb_db):

    ref = fb_db.reference('projectDrafts/')

    with open('sample_project_drafts.json') as f:
        sample_project_drafts = json.load(f)

    # upload sample data to firebaseio.com/imports
    project_draft_ids = []
    for project in sample_project_drafts:
        project_draft_id = ref.push(sample_project_drafts[project]).key
        project_draft_ids.append(project_draft_id)
        print(
                f'Uploaded a new sample project draft with the id: '
                f'{project_draft_id} '
                )

    save_project_draft_ids_to_disk(project_draft_ids)

    # for import_key in uploaded_project_keys:
    #     fb_db.update(
    #         {
    #             "imports/{}/key".format(import_key): auth.get_submission_key()
    #         }
    #     )


def create_user(fb_db):
    ref = fb_db.reference('users/')
    user = {
            "distance": 0,
            "username": "test user",
            "contributedCount": 0
            }
    user_id = ref.push(user).key
    save_user_id(user_id)


def save_project_draft_ids_to_disk(project_draft_ids):
    filename = 'project_ids.pickle'
    if os.path.isfile(filename):
        with open(filename, 'rb') as f:
            existing_project_draft_ids = pickle.load(f)
        project_draft_ids = existing_project_draft_ids + project_draft_ids

    with open(filename, 'wb') as f:
        pickle.dump(project_draft_ids, f)


def save_user_id(user_id):
    filename = 'user_ids.pickle'
    if os.path.isfile(filename):
        with open(filename, 'rb') as f:
            existing_user_ids = pickle.load(f)
        user_id = existing_user_ids + user_id

    with open(filename, 'wb') as f:
        pickle.dump(user_id, f)


if __name__ == '__main__':
    fb_db = auth.firebaseDB()
    create_project_drafts_in_firebase(fb_db)
    create_user(fb_db)
