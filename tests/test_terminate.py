import pickle
import os.path
from mapswipe_workers.basic import BaseFunctions


def delete_sample_date_from_firebase():
    firebase, postgres = BaseFunctions.get_environment('production')
    fb_db = firebase.database()
    fb_db.child('imports').set({})

    # if os.path.isfile('firebase_imports_keys.pickle'):
    #     with open('firebase_imports_keys.pickle', 'rb') as f:
    #         keys = pickle.load(f)
    #     os.remove('firebase_imports_keys.pickle')
    # else:
    #     raise FileNotFoundError

    # for key in keys:
    #     print(key)
    #     fb_db.child('imports').child(key).remove()


def delete_sample_groups_from_firebase():
    firebase, postgres = BaseFunctions.get_environment('production')
    fb_db = firebase.database()
    fb_db.child('groups').set({})
    fb_db.child('projects').set({})
    #os.remove('firebase_imports_keys.pickle')


if __name__ == '__main__':
    delete_sample_date_from_firebase()
    delete_sample_groups_from_firebase()
    # TODO: remove groups and projects
