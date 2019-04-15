import os
import json
import logging
import logging.config
from xdg.BaseDirectory import xdg_config_home
from logging.handlers import TimedRotatingFileHandler


ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
# ROOT_DIR = '/python-mapswipe-workers'

CONFIG_PATH = f'{xdg_config_home}/mapswipe_workers/configuration.json'
# CONFIG_PATH = os.path.abspath(
#         os.path.join(ROOT_DIR, './cfg/configuration.json')
#         )

SERVICE_ACCOUNT_KEY_PATH = f'{xdg_config_home}/mapswipe_workers/serviceAccountKey.json'
# SERVICE_ACCOUNT_KEY_PATH = os.path.abspath(
#         os.path.join(ROOT_DIR, 'cfg', 'serviceAccountKey.json')
#         )

DATA_PATH = '/var/lib/mapswipe_workers/'
# DATA_PATH = os.path.abspath(
#         os.path.join(ROOT_DIR, './data/')
#         )

LOGGING_CONFIG_PATH = os.path.abspath(
        os.path.join(ROOT_DIR, 'logging.cfg')
        )

logging.config.fileConfig(
        fname=LOGGING_CONFIG_PATH,
        disable_existing_loggers=True
        )
logger = logging.getLogger('Mapswipe Workers')


class CustomError(Exception):
    pass
