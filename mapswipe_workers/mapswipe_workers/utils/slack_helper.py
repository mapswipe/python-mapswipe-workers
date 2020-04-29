import slack
from mapswipe_workers.definitions import logger
from mapswipe_workers import auth
from mapswipe_workers.config import SLACK_CHANNEL, SLACK_TOKEN


def send_slack_message(message_type: str, project_name: str, project_id: str = None):
    """Initialize slack client with values provided in environment."""
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
        slack_client.chat_postMessage(channel=SLACK_CHANNEL, text=message)
    elif message_type == "fail":
        message = (
            "### PROJECT CREATION FAILED ###\n"
            + "Project Name: {0}\n".format(project_name)
            + "Project draft is deleted."
        )
        slack_client.chat_postMessage(channel=SLACK_CHANNEL, text=message)
    elif message_type == "notification_90":
        message = (
            "### ALMOST THERE! PROJECT REACHED 90% ###\n"
            + "Project Name: {0}\n".format(project_name)
            + "Project Id: {0}\n\n".format(project_id)
            + "Get your next projects ready."
        )
        slack_client.chat_postMessage(channel="mapswipe_managers", text=message)
    elif message_type == "notification_100":
        message = (
            "### GREAT! PROJECT REACHED 100% ###\n"
            + "Project Name: {0}\n".format(project_name)
            + "Project Id: {0}\n\n".format(project_id)
            + "You can set this project to 'finished' "
            + "and activate another one."
        )
        slack_client.chat_postMessage(channel="mapswipe_managers", text=message)
    else:
        # TODO: Raise an Exception
        pass


def send_progress_notification(project_id: int):
    """Send progress notification to project managers in Slack."""
    fb_db = auth.firebaseDB()
    progress = fb_db.reference(f"v2/projects/{project_id}/progress").get()
    project_name = fb_db.reference(f"v2/projects/{project_id}/name").get()
    notification_90_sent = fb_db.reference(
        f"v2/projects/{project_id}/notification_90_sent"
    ).get()
    notification_100_sent = fb_db.reference(
        f"v2/projects/{project_id}/notification_100_sent"
    ).get()
    logger.info(
        f"{project_id} - progress: {progress},"
        f"notifications: {notification_90_sent} {notification_100_sent}"
    )

    if progress >= 90 and not notification_90_sent:
        # send notification and set value in firebase
        fb_db.reference(f"v2/projects/{project_id}/notification_90_sent").set(True)
        send_slack_message("notification_90", project_name, project_id)

    if progress >= 100 and not notification_100_sent:
        # send notification and set value in firebase
        fb_db.reference(f"v2/projects/{project_id}/notification_100_sent").set(True)
        send_slack_message("notification_100", project_name, project_id)
