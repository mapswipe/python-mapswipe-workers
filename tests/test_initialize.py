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
    uploaded_project_keys = []
    for data in sample_data:
        uploaded_project_keys.append(
                fb_db.child("imports").push(sample_data[data])['name']
                )

    # save all keys to disk
    filename = 'firebase_uploaded_projects.pickle'
    if os.path.isfile(filename):
        with open(filename, 'rb') as f:
            already_uploaded_project_keys = pickle.load(f)
        uploaded_project_keys = already_uploaded_project_keys + uploaded_project_keys
    with open(filename, 'wb') as f:
        pickle.dump(uploaded_project_keys, f)


if __name__ == '__main__':
    upload_sample_data_to_firebase()
    with open('firebase_uploaded_projects.pickle', 'rb') as f:
        keys = pickle.load(f)
    print(keys)
    print("Everything passed")
