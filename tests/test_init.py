import json
from mapswipe_workers.basic import BaseFunctions


def upload_sample_data_to_firebase():
    firebase, postgres = BaseFunctions.get_environment('development')


if __name__ == '__main__':
    upload_sample_data_to_firebase()
