import json
from mapswipe_workers.basic import BaseFunctions


def upload_sample_data_to_firebase():
    firebase, postgres = BaseFunctions.get_environment('production')

    with open('sample_data.json') as f:
        sample_data = json.load(f) 

    fb_db = firebase.database()
    fb_db.child("imports").set(sample_data)


if __name__ == '__main__':
    upload_sample_data_to_firebase()
    print("Everything passed")
