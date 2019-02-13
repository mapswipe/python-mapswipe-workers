import os
import json


# ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = '/home/matthias/Arbeit/projekte/python-mapswipe-workers'

# CONFIG_PATH = os.path.abspath(os.path.join(ROOT_DIR, 'configuration.json'))
CONFIG_PATH = os.path.abspath(os.path.join(ROOT_DIR, 'cfg', 'configuration.json'))

# SERVICE_ACCOUNT_KEY_PATH = os.path.abspath(os.path.join(ROOT_DIR, 'service_account_key'))

# DATA_PATH = get_data_path()
DATA_PATH = os.path.abspath(os.path.join(ROOT_DIR, 'data'))


# def get_data_path():
#     '''reads data path from config'''
#     with open(CONFIG_PATH) as config_file:
#         config = json.load(config_file)
#     return config['mapswipe_workers']['data_path']


class CustomError(Exception):
    pass
