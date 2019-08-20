import os
import json
import logging
import logging.config
from logging.handlers import TimedRotatingFileHandler


ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

CONFIG_DIR = os.path.abspath(
        '/usr/share/config/mapswipe_workers/'
        )

CONFIG_PATH = os.path.join(
        CONFIG_DIR,
        'configuration.json'
        )

SERVICE_ACCOUNT_KEY_PATH = os.path.join(
        CONFIG_DIR,
        'serviceAccountKey.json'
        )

LOGGING_CONFIG_PATH = os.path.join(
        CONFIG_DIR,
        'logging.cfg'
        )

DATA_PATH = os.path.abspath(
        '/var/lib/mapswipe_workers/'
        )

logging.config.fileConfig(
        fname=LOGGING_CONFIG_PATH,
        disable_existing_loggers=True
        )
logger = logging.getLogger('Mapswipe Workers')


class CustomError(Exception):
    pass
