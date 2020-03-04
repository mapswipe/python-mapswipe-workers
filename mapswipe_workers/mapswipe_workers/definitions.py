import logging
import logging.config
import os

import sentry_sdk
from xdg import XDG_DATA_HOME
from mapswipe_workers.config import SENTRY_DSN


class CustomError(Exception):
    pass


IMAGE_URL = {
    "bing": "https://ecn.t0.tiles.virtualearth.net/tiles/a{quad_key}.jpeg?g=7505&mkt=en-US&token={key}",
    "mapbox": "https://d.tiles.mapbox.com/v4/mapbox.satellite/{z}/{x}/{y}.jpg?access_token={key}",
    "maxar_premium": "https://services.digitalglobe.com/earthservice/tmsaccess/tms/1.0.0/DigitalGlobe%3AImageryTileService@EPSG%3A3857@jpg/{z}/{x}/{y}.jpg?connectId={key}",
    "maxar_standard": "https://services.digitalglobe.com/earthservice/tmsaccess/tms/1.0.0/DigitalGlobe%3AImageryTileService@EPSG%3A3857@jpg/{z}/{x}/{y}.jpg?connectId={key}",
    "esri": "https://services.arcgisonline.com/arcgis/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
    "esri_beta": "https://clarity.maptiles.arcgis.com/arcgis/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
    "sinergise": "https://services.sentinel-hub.com/ogc/wmts/{key}?request=getTile&tilematrixset=PopularWebMercator256&tilematrix={z}&tilecol={x}&tilerow={y}&layer={layer}",
}

DATA_PATH = os.path.join(XDG_DATA_HOME, "mapswipe_workers")
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
LOGGING_CONFIG_PATH = os.path.join(ROOT_DIR, "logging.cfg")
LOGGING_FILE_PATH = os.path.join(DATA_PATH, "mapswipe_workers.log")

logging.config.fileConfig(
    fname=LOGGING_CONFIG_PATH,
    defaults={"logfilename": LOGGING_FILE_PATH},
    disable_existing_loggers=True,
)
logger = logging.getLogger("Mapswipe Workers")

try:
    sentry_sdk.init(SENTRY_DSN)
except KeyError:
    logger.info(
        "No configuration for Sentry was found. Continue without Sentry integration."
    )
sentry = sentry_sdk
