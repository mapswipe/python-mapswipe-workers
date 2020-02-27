"""Initialize slack client with values provided by the config file"""

import json

import slack

from mapswipe_workers.definitions import CONFIG_PATH, logger


def send_slack_message(message_type: str, project_name: str, project_id: str = None):

    with open(CONFIG_PATH) as config_file:
        config = json.load(config_file)
    try:
        slack_channel = config["slack"]["channel"]
    except KeyError:
        logger.info(
            "No configuration for Slack was found. "
            + "No '{0}' Slack message was sent.".format(message_type)
        )
        return None
    slack_client = slack.WebClient(token=config["slack"]["token"])

    if message_type == "success":
        message = (
            "### PROJECT CREATION SUCCESSFUL ###\n"
            + "Project Name: {0}\n".format(project_name)
            + "Project Id: {0}\n\n".format(project_id)
            + "Make sure to activate the project using the manager dashboard.\n"
            + "Happy Swiping. :)"
        )
    elif message_type == "fail":
        message = (
            "### PROJECT CREATION FAILED ###\n"
            + "Project Name: {0}\n".format(project_name)
            + "Project draft is deleted."
        )
    else:
        # TODO: Raise an Exception
        pass

    slack_client.chat_postMessage(channel=slack_channel, text=message)
