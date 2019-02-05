import json
from mapswipe_workers.basic import BaseFunctions


def upload_sample_data_to_firebase():
    firebase, postgres = BaseFunctions.get_environment('development')

    with open('sample_data') as f:
        sample_data = json.load(f)


if __name__ == '__main__':
    upload_sample_data_to_firebase()
