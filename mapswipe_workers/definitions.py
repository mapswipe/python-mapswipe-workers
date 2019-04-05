import os
import json
import logging
import logging.config


ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
# CONFIG_PATH = os.path.abspath(os.path.join(ROOT_DIR, '/cfg/configuration.json'))
CONFIG_PATH = os.path.join(ROOT_DIR, 'cfg', 'configuration.json')
# SERVICE_ACCOUNT_KEY_PATH = os.path.abspath(os.path.join(ROOT_DIR, '/cfg/serviceAccountKey.json'))
SERVICE_ACCOUNT_KEY_PATH = os.path.join(ROOT_DIR, 'cfg', 'serviceAccountKey.json')
DATA_PATH = os.path.join(ROOT_DIR, 'data')
# DATA_PATH = get_data_path()
LOGGING_CONFIG_PATH = os.path.join(ROOT_DIR, 'logging.cfg')

logging.config.fileConfig(
        fname=LOGGING_CONFIG_PATH,
        disable_existing_loggers=True
        )
logger = logging.getLogger('Mapswipe Workers')

# def get_data_path():
#     '''reads data path from config'''
#     with open(CONFIG_PATH) as config_file:
#         config = json.load(config_file)
#     return config['mapswipe_workers']['data_path']


class CustomError(Exception):
    pass
