import shutil
import os
from mapswipe_workers.definitions import ROOT_DIR
from mapswipe_workers.definitions import CONFIG_PATH


def copy_config(source_path=os.path.abspath(
        os.path.join(ROOT_DIR, '../cfg/configuration.json')
        )):
    '''
    Copy user provided configuration into root of mapswipe_workers module for consistent access.
    '''
    shutil.copyfile(source_path, CONFIG_PATH)
