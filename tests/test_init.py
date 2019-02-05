import json
from mapswipe_workers.definitions import CONFIG_PATH

def upload_sample_data_to_firebase():
    with open(CONFIG_PATH) as f:
        config = json.load(f)
    print(config)

if __name__ == '__main__':
    upload_sample_data_to_firebase()
