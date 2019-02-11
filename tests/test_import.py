import os
import pickle
from mapswipe_workers.basic import BaseFunctions


def import_process():
    firebase, postgres = BaseFunctions.get_environment('production')
    fb_db = firebase.database()

    # get all keys from firebaseio.com/groups and /projects
    # before running import

    all_groups_pre = fb_db.child("groups").shallow().get().val()
    all_projects_pre = fb_db.child("projects").shallow().get().val()

    if all_groups_pre is None:
        all_groups_pre = list()
    else:
        all_groups_pre = list(all_groups_pre)

    if all_projects_pre is None:
        all_projects_pre = list()
    else:
        all_projects_pre = list(all_projects_pre)

    BaseFunctions.run_import('production')

    # get all keys from firebaseio.com/groups and /projects
    # after running import
    all_groups_post = list(fb_db.child("groups").shallow().get().val())
    all_projects_post = list(fb_db.child("projects").shallow().get().val())

    groups_keys = list(set(all_groups_post) - set(all_groups_pre))
    projects_keys = list(set(all_projects_post) - set(all_projects_pre))

    # save all keys to disk
    filename = 'firebase_groups_keys.pickle'
    if os.path.isfile(filename):
        with open(filename, 'rb') as f:
            data = pickle.load(f)
        groups_keys = data + groups_keys

    with open(filename, 'wb') as f:
        pickle.dump(groups_keys, f)

    filename = 'firebase_projects_keys.pickle'
    if os.path.isfile(filename):
        with open(filename, 'rb') as f:
            data = pickle.load(f)
        projects_keys = data + projects_keys

    with open(filename, 'wb') as f:
        pickle.dump(projects_keys, f)

# TODO: check if everything has been created correctly in firebase and postgres


if __name__ == '__main__':
    import_process()
    print("Everything passed")
