import shutil
from mapswipe_workers.definitions import CONFIG_PATH
from mapswipe_workers.definitions import SERVICE_ACCOUNT_KEY_PATH


def copy_config(source_path):
    '''
    Copy user provided configuration into root of mapswipe_workers module for consistent access.
    '''
    shutil.copyfile(source_path, CONFIG_PATH)


def copy_firebase_service_account_key(source_dir)
    '''
    Copy user provided firebase service key into root of mapswipe_workers module for constistent access.
    '''
    with open(CONFIG_PATH, 'r') as config:
        config = json.load(config)
        filename = config['firebase']['service_account']
    if os.path.isfile(filename):
        shutil.copyfile(filename, SERVICE_ACCOUNT_KEY_PATH)
    else:
        source_path = os.path.abspath(os.path.join(source_dir, filename))
        shutil.copyfile(source_dir, SERVICE_ACCOUNT_KEY_PATH)
