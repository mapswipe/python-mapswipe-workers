import os
import pickle
import json

from mapswipe_workers.basic import auth


def create_project_drafts_in_firebase(ref):

    with open('sample_project_drafts.json') as f:
        sample_project_drafts = json.load(f)

    # upload sample data to firebaseio.com/imports
    project_draft_ids = []
    for project in sample_project_drafts:
        project_draft_ids.append(
                ref.push(sample_project_drafts[project]).key
                )

    save_project_draft_ids_to_disk(project_draft_ids)

    # for import_key in uploaded_project_keys:
    #     fb_db.update(
    #         {
    #             "imports/{}/key".format(import_key): auth.get_submission_key()
    #         }
    #     )


def save_project_draft_ids_to_disk(project_draft_ids):
    filename = 'project_draft_ids.pickle'
    if os.path.isfile(filename):
        with open(filename, 'rb') as f:
            existing_project_draft_ids = pickle.load(f)
        project_draft_ids = existing_project_draft_ids + project_draft_ids

    with open(filename, 'wb') as f:
        pickle.dump(project_draft_ids, f)


if __name__ == '__main__':

    db = auth.firebaseDB()

    ref = db.reference('projectDrafts/')

    create_project_drafts_in_firebase(ref)
