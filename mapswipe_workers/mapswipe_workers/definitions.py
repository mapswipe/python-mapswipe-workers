import json
import logging
import logging.config
import os

import sentry_sdk

from mapswipe_workers.project_types.build_area.build_area_project import (
    BuildAreaProject,
)
from mapswipe_workers.project_types.change_detection.change_detection_project import (
    ChangeDetectionProject,
)
from mapswipe_workers.project_types.footprint.footprint_project import FootprintProject


class CustomError(Exception):
    pass


def load_config(CONFIG_PATH) -> dict:
    """Read the configuration file."""
    with open(CONFIG_PATH) as f:
        return json.load(f)


ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

CONFIG_DIR = os.path.abspath("/usr/share/config/mapswipe_workers/")

CONFIG_PATH = os.path.join(CONFIG_DIR, "configuration.json")

CONFIG = load_config(CONFIG_PATH)

SERVICE_ACCOUNT_KEY_PATH = os.path.join(CONFIG_DIR, "serviceAccountKey.json")

LOGGING_CONFIG_PATH = os.path.join(CONFIG_DIR, "logging.cfg")

DATA_PATH = os.path.abspath("/var/lib/mapswipe_workers/")

PROJECT_TYPE_CLASSES = {
    1: BuildAreaProject,
    2: FootprintProject,
    3: ChangeDetectionProject,
}

PROJECT_TYPE_NAMES = {
    1: BuildAreaProject.project_type_name,
    2: FootprintProject.project_type_name,
    3: ChangeDetectionProject.project_type_name,
}

logging.config.fileConfig(fname=LOGGING_CONFIG_PATH, disable_existing_loggers=True)
logger = logging.getLogger("Mapswipe Workers")

sentry_sdk.init(CONFIG["sentry"]["dsn"])
sentry = sentry_sdk
