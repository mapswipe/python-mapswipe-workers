import json
import logging
import logging.config
import os

import sentry_sdk
from xdg import XDG_CONFIG_HOME, XDG_DATA_HOME


class CustomError(Exception):
    pass


def load_config(CONFIG_PATH) -> dict:
    """Read the configuration file."""
    with open(CONFIG_PATH) as f:
        return json.load(f)


ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

CONFIG_DIR = os.path.join(XDG_CONFIG_HOME, "mapswipe_workers/")

CONFIG_PATH = os.path.join(CONFIG_DIR, "configuration.json")

CONFIG = load_config(CONFIG_PATH)

SERVICE_ACCOUNT_KEY_PATH = os.path.join(CONFIG_DIR, "serviceAccountKey.json")

DATA_PATH = os.path.join(XDG_DATA_HOME, "mapswipe_workers/")

LOGGING_CONFIG_PATH = os.path.join(ROOT_DIR, "logging.cfg")

LOGGING_FILE_PATH = os.path.join(DATA_PATH, "mapswipe_workers.log")

logging.config.fileConfig(
    fname=LOGGING_CONFIG_PATH,
    defaults={"logfilename": LOGGING_FILE_PATH},
    disable_existing_loggers=True,
)
logger = logging.getLogger("Mapswipe Workers")

try:
    sentry_sdk.init(CONFIG["sentry"]["dsn"])
except KeyError:
    logger.info(
        "No configuration for Sentry was found. Continue without Sentry integration."
    )
sentry = sentry_sdk
