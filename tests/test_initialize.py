import json
import pickle
import os.path
from mapswipe_workers.basic import BaseFunctions
from mapswipe_workers.utils import path_helper


def upload_sample_data_to_firebase():
    
    path_helper.copy_config()

    firebase, postgres = BaseFunctions.get_environment('production')
    fb_db = firebase.database()

    # get all keys from firebaseio.com/imports before upload
    all_imports_pre = fb_db.child("imports").shallow().get().val()

    if all_imports_pre is None:
        all_imports_pre = []
    else:
        all_imports_pre = list(all_imports_pre)

    with open('sample_data.json') as f:
        sample_data = json.load(f)

    # upload sample data to firebaseio.com/imports
    for data in sample_data:
        fb_db.child("imports").push(sample_data[data])

    # get all keys from firebaseio.com/imports after upload
    all_imports_post = list(fb_db.child("imports").shallow().get().val())

    keys = list(set(all_imports_post) - set(all_imports_pre))

    # save all keys to disk
    filename = 'firebase_imports_keys.pickle'
    if os.path.isfile(filename):
        with open(filename, 'rb') as f:
            data = pickle.load(f)
        keys = data + keys

    with open(filename, 'wb') as f:
        pickle.dump(keys, f)


if __name__ == '__main__':
    upload_sample_data_to_firebase()
    with open('firebase_imports_keys.pickle', 'rb') as f:
        keys = pickle.load(f)
    print(keys)
    print("Everything passed")
