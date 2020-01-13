"""Initialize slack client with values provided by the config file"""

import json
import slack

from mapswipe_workers.definitions import CONFIG_PATH


with open(CONFIG_PATH) as config_file:
    config = json.load(config_file)
    slack_channel = config["slack"]["channel"]
    slack_client = slack.WebClient(token=config["slack"]["token"])
