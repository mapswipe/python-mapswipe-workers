import os
import json


ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.abspath(os.path.join(ROOT_DIR, 'configuration.json'))
DATA_PATH = os.path.abspath(os.path.join(ROOT_DIR, '..', 'data'))
# DATA_PATH = get_data_path()


# def get_data_path():
#     '''reads data path from config'''
#     with open(CONFIG_PATH) as config_file:
#         config = json.load(config_file)
#     return config['mapswipe_workers']['data_path']


class CustomError(Exception):
    pass
