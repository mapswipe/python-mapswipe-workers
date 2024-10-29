import logging.config
import os
from enum import Enum

import sentry_sdk
from xdg import XDG_DATA_HOME

from mapswipe_workers.config import SENTRY_DSN

DATA_PATH = os.path.join(XDG_DATA_HOME, "mapswipe_workers")
if not os.path.exists(DATA_PATH):
    os.makedirs(DATA_PATH)
LOGGING_FILE_PATH = os.path.join(DATA_PATH, "mapswipe_workers.log")

OHSOME_API_LINK = "https://api.ohsome.org/v1/"
OSM_API_LINK = "https://www.openstreetmap.org/api/0.6/"
OSMCHA_API_LINK = "https://osmcha.org/api/v1/"
OSMCHA_API_KEY = os.environ["OSMCHA_API_KEY"]

# number of geometries for project geometries
MAX_INPUT_GEOMETRIES = 10

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": True,
    "formatters": {
        "standard": {
            "format": "%(asctime)s - %(levelname)s - %(filename)s - %(funcName)s - %(message)s"  # noqa: E501
        },
    },
    "handlers": {
        "console": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "formatter": "standard",
        },
        "file": {
            "level": "INFO",
            "class": "logging.handlers.TimedRotatingFileHandler",
            "formatter": "standard",
            "filename": LOGGING_FILE_PATH,
            "when": "D",
            "interval": 1,
            "backupCount": 14,
        },
    },
    "loggers": {
        "root": {"handlers": ["console"], "level": "INFO"},
        "mapswipe": {
            "handlers": ["console", "file"],
            "level": "INFO",
            "propagate": False,
        },
    },
}

logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger("mapswipe")


try:
    sentry_sdk.init(SENTRY_DSN)
except KeyError:
    logger.info(
        "No configuration for Sentry was found. Continue without Sentry integration."
    )
sentry = sentry_sdk


IMAGE_URLS = {
    "bing": (
        "https://ecn.t0.tiles.virtualearth.net"
        + "/tiles/a{quad_key}.jpeg?g=7505&token={key}"
    ),
    "mapbox": (
        "https://d.tiles.mapbox.com"
        + "/v4/mapbox.satellite/{z}/{x}/{y}.jpg?access_token={key}"
    ),
    "maxar_premium": (
        "https://services.digitalglobe.com"
        + "/earthservice/tmsaccess/tms/1.0.0/"
        + "DigitalGlobe%3AImageryTileService@EPSG%3A3857@jpg/"
        + "{z}/{x}/{y}.jpg?connectId={key}"
    ),
    "maxar_standard": (
        "https://services.digitalglobe.com"
        + "/earthservice/tmsaccess/tms/1.0.0/"
        + "DigitalGlobe%3AImageryTileService@EPSG%3A3857@jpg/"
        + "{z}/{x}/{y}.jpg?connectId={key}"
    ),
    "esri": (
        "https://services.arcgisonline.com"
        + "/arcgis/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"
    ),
    "esri_beta": (
        "https://clarity.maptiles.arcgis.com"
        + "/arcgis/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"
    ),
    "sinergise": (
        "https://services.sentinel-hub.com"
        + "/ogc/wmts/{key}?request=getTile&tilematrixset=PopularWebMercator256&"
        + "tilematrix={z}&tilecol={x}&tilerow={y}&layer={layer}"
    ),
}


class CustomError(Exception):
    pass


class MessageType(Enum):
    """The different types of messages sent via Slack."""

    SUCCESS = 1
    FAIL = 2
    NOTIFICATION_90 = 3
    NOTIFICATION_100 = 4
    PROJECT_STATUS_FINISHED = 5
    PROJECT_STATUS_ACTIVE = 6


class ProjectType(Enum):
    """
    Definition of Project Type names, identifiers and constructors.

    There are different project types with the same constructor.
    Get the class constructor of a project type with:
    ProjectType(1).constructor
    """

    BUILD_AREA = 1
    FOOTPRINT = 2
    CHANGE_DETECTION = 3
    COMPLETENESS = 4
    MEDIA_CLASSIFICATION = 5
    DIGITIZATION = 6
    STREET = 7

    @property
    def constructor(self):
        # Imports are first made once this method get called to avoid circular imports.
        from mapswipe_workers.project_types import (
            ChangeDetectionProject,
            ClassificationProject,
            CompletenessProject,
            DigitizationProject,
            FootprintProject,
            MediaClassificationProject,
            StreetProject,
        )

        project_type_classes = {
            1: ClassificationProject,
            2: FootprintProject,
            3: ChangeDetectionProject,
            4: CompletenessProject,
            5: MediaClassificationProject,
            6: DigitizationProject,
            7: StreetProject,
        }
        return project_type_classes[self.value]

    @property
    def tutorial(self):
        # Imports are first made once this method get called to avoid circular imports.
        from mapswipe_workers.project_types import (
            ChangeDetectionTutorial,
            ClassificationTutorial,
            CompletenessTutorial,
            FootprintTutorial,
        )

        project_type_classes = {
            1: ClassificationTutorial,
            2: FootprintTutorial,
            3: ChangeDetectionTutorial,
            4: CompletenessTutorial,
        }
        return project_type_classes[self.value]
