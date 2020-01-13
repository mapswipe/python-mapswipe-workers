"""Initialize sentry client with values provided by the config file"""

import json
import sentry_sdk

from mapswipe_workers.definitions import CONFIG_PATH


with open(CONFIG_PATH) as config_file:
    config = json.load(config_file)
    sentry_url = config["sentry"]["dsn"]
    sentry_sdk.init(sentry_url)
