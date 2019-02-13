import json
import pickle
import os.path
from mapswipe_workers.basic import BaseFunctions


def upload_sample_data_to_firebase():
    firebase, postgres = BaseFunctions.get_environment('production')
    fb_db = firebase.database()

    with open('sample_data.json') as f:
        sample_data = json.load(f)

    # upload sample data to firebaseio.com/imports
    uploaded_projects_keys = []
    for data in sample_data:
        uploaded_projects_keys.append(
                fb_db.child("imports").push(sample_data[data])
                )['name']

    # save all keys to disk
    filename = 'firebase_uploaded_projects_keys.pickle'
    if os.path.isfile(filename):
        with open(filename, 'rb') as f:
            already_uploaded_projects_keys = pickle.load(f)
        uploaded_projects_keys = already_uploaded_projects_keys\
            + uploaded_projects_keys
    with open(filename, 'wb') as f:
        pickle.dump(uploaded_projects_keys, f)


if __name__ == '__main__':
    upload_sample_data_to_firebase()
    with open('firebase_imports_keys.pickle', 'rb') as f:
        keys = pickle.load(f)
    print(keys)
    print("Everything passed")
