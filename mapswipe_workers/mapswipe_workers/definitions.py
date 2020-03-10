import logging
import logging.config
import os

import sentry_sdk
from xdg import XDG_DATA_HOME
from mapswipe_workers.config import SENTRY_DSN


class CustomError(Exception):
    pass


IMAGE_URL = {
    "bing": (
        "https://ecn.t0.tiles.virtualearth.net",
        "/tiles/a{quad_key}.jpeg?g=7505&mkt=en-US&token={key}",
    ),
    "mapbox": (
        "https://d.tiles.mapbox.com",
        "/v4/mapbox.satellite/{z}/{x}/{y}.jpg?access_token={key}",
    ),
    "maxar_premium": (
        "https://services.digitalglobe.com",
        "/earthservice/tmsaccess/tms/1.0.0/",
        "DigitalGlobe%3AImageryTileService@EPSG%3A3857@jpg/",
        "{z}/{x}/{y}.jpg?connectId={key}",
    ),
    "maxar_standard": (
        "https://services.digitalglobe.com",
        "/earthservice/tmsaccess/tms/1.0.0/",
        "DigitalGlobe%3AImageryTileService@EPSG%3A3857@jpg/",
        "{z}/{x}/{y}.jpg?connectId={key}",
    ),
    "esri": (
        "https://services.arcgisonline.com",
        "/arcgis/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
    ),
    "esri_beta": (
        "https://clarity.maptiles.arcgis.com",
        "/arcgis/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
    ),
    "sinergise": (
        "https://services.sentinel-hub.com",
        "/ogc/wmts/{key}?request=getTile&tilematrixset=PopularWebMercator256&",
        "tilematrix={z}&tilecol={x}&tilerow={y}&layer={layer}",
    ),
}

DATA_PATH = os.path.join(XDG_DATA_HOME, "mapswipe_workers")
LOGGING_FILE_PATH = os.path.join(DATA_PATH, "mapswipe_workers.log")

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": True,
    "formatters": {
        "mapswipeFormatter": {
            "format": (
                "%(asctime)s - %(levelname)s -",
                "%(filename)s - %(funcName)s - %(message)s",
            )
        }
    },
    "handlers": {
        "consoleHandler": {
            "class": "logging.StreamHandler",
            "level": "INFO",
            "formatter": "mapswipeFormatter",
            "stream": "ext:://sys.stdout",
        },
        "fileHandler": {
            "class": "logging.handlers.TimedRotatingFileHandler",
            "level": "INFO",
            "formatter": "mapswipeFormatter",
            "filename": LOGGING_FILE_PATH,
            "when": "D",
            "interval": 1,
            "backupCount": 14,
        },
    },
    "loggers": {
        "root": {"handlers": ["consoleHandler"], "level": "INFO"},
        "mapswipeLogger": {
            "handlers": ["consoleHandler", "fileHandler"],
            "level": "INFO",
            "qualname": "mapswipeLogger",
            "propagate": False,
        },
    },
}

logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger("Mapswipe Workers")

try:
    sentry_sdk.init(SENTRY_DSN)
except KeyError:
    logger.info(
        "No configuration for Sentry was found. Continue without Sentry integration."
    )
sentry = sentry_sdk
