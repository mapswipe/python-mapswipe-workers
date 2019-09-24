import pickle
import os

from mapswipe_workers import auth
from mapswipe_workers.definitions import DATA_PATH
from mapswipe_workers.utils import user_management


def delete_sample_data_from_firebase(fb_db, project_id):
    ref = fb_db.reference(f'v2/results/{project_id}')
    ref.set({})
    ref = fb_db.reference(f'v2/tasks/{project_id}')
    ref.set({})
    ref = fb_db.reference(f'v2/groups/{project_id}')
    ref.set({})
    ref = fb_db.reference(f'v2/projects/{project_id}')
    ref.set({})
    ref = fb_db.reference(f'v2/projectDrafts/{project_id}')
    ref.set({})

    users = fb_db.reference('users').get()
    for user_id, user in users.items():
        ref = fb_db.reference(f'v2/users/{user_id}/contributions/{project_id}')
        ref.set({})

    print(
            f'Firebase: '
            f'deleted projectDraft, project, groups, tasks and results '
            f'with the project id: {project_id}'
            )


if __name__ == '__main__':
    fb_db = auth.firebaseDB()

    projects = fb_db.reference('v2/projects/').get()
    projects_to_delete = set([])
    projects_to_keep = set([])
    for project_id, project in projects.items():
        if project['status'] == 'inactive':
            projects_to_delete.add(project_id)
        else:
            projects_to_keep.add(project_id)

    print(f'projects to keep {projects_to_keep}')
    print(f'projects to delete {projects_to_delete}')

    for project_id in projects_to_delete:
        delete_sample_data_from_firebase(fb_db, project_id)

    users = fb_db.reference('v2/users').get()
    users_to_delete = set([])
    for user_id, user in users.items():
        try:
            if user['username'].startswith('test_'):
                print(user['username'])
                users_to_delete.add(user_id)
        except:
            pass

    for user_id in users_to_delete:
        ref = fb_db.reference(f'v2/users/{user_id}')
        ref.set({})
        print('deleted user in firebase')



