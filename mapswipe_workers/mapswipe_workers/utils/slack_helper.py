"""Initialize slack client with values provided by the config file"""

import slack

from mapswipe_workers.definitions import logger
from mapswipe_workers.config import SLACK_CHANNEL, SLACK_TOKEN


def send_slack_message(message_type: str, project_name: str, project_id: str = None):
    print(SLACK_TOKEN)
    print(SLACK_CHANNEL)
    if SLACK_TOKEN is None or SLACK_CHANNEL is None:
        logger.info(
            "No configuration for Slack was found. "
            + "No '{0}' Slack message was sent.".format(message_type)
        )
        return None

    slack_client = slack.WebClient(token=SLACK_TOKEN)

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

    slack_client.chat_postMessage(channel=SLACK_CHANNEL, text=message)
