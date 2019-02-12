import shutil
from mapswipe_workers.definitions import CONFIG_PATH


def copy_config(source_path):
    '''
    Copy user provided configuration into root of mapswipe_workers module for consistent access.
    '''
    shutil.copyfile(source_path, CONFIG_PATH)
