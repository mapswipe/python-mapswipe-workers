import os
import pickle
import json

from mapswipe_workers.basic import auth


def create_project_drafts_in_firebase(ref):

    with open('sample_project_drafts.json') as f:
        sample_project_drafts = json.load(f)

    # upload sample data to firebaseio.com/imports
    project_draft_keys = []
    for project in sample_project_drafts:
        project_draft_keys.append(
                ref.push(sample_project_drafts[project]).key
                )

    save_project_draft_keys_to_disk(project_draft_keys)

    # for import_key in uploaded_project_keys:
    #     fb_db.update(
    #         {
    #             "imports/{}/key".format(import_key): auth.get_submission_key()
    #         }
    #     )


def save_project_draft_keys_to_disk(project_draft_keys):
    filename = 'project_draft_keys.pickle'
    if os.path.isfile(filename):
        with open(filename, 'rb') as f:
            existing_project_draft_keys = pickle.load(f)
        project_draft_keys = existing_project_draft_keys + project_draft_keys

    with open(filename, 'wb') as f:
        pickle.dump(project_draft_keys, f)


if __name__ == '__main__':

    db = auth.firebaseDB()

    ref = db.reference('projectDrafts/')

    create_project_drafts_in_firebase(ref)
