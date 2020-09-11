import slack
from mapswipe_workers.definitions import logger
from mapswipe_workers import auth
from mapswipe_workers.config import SLACK_CHANNEL, SLACK_TOKEN
from mapswipe_workers.definitions import MessageType


def send_slack_message(
    message_type: MessageType, project_name: str, project_id: str = None
):
    """Initialize slack client with values provided in environment."""
    if SLACK_TOKEN is None or SLACK_CHANNEL is None:
        logger.info(
            "No configuration for Slack was found. "
            + "No '{0}' Slack message was sent.".format(message_type)
        )
        return None

    slack_client = slack.WebClient(token=SLACK_TOKEN)

    if message_type == MessageType.SUCCESS:
        message = (
            "### PROJECT CREATION SUCCESSFUL ###\n"
            + f"Project Name: {project_name}\n"
            + f"Project Id: {project_id}\n\n"
            + "Make sure to activate the project with the manager dashboard.\n"
            + "Happy Swiping. :)"
        )
        slack_client.chat_postMessage(channel=SLACK_CHANNEL, text=message)
    elif message_type == MessageType.FAIL:
        message = (
            "### PROJECT CREATION FAILED ###\n"
            + f"Project Name: {project_name}\n"
            + "Project draft is deleted."
        )
        slack_client.chat_postMessage(channel=SLACK_CHANNEL, text=message)
    elif message_type == MessageType.NOTIFICATION_90:
        message = (
            "### ALMOST THERE! PROJECT REACHED 90% ###\n"
            + f"Project Name: {project_name}\n"
            + f"Project Id: {project_id}\n\n"
            + "Get your next projects ready."
        )
        slack_client.chat_postMessage(
            channel="mapswipe_managers", text=message)
    elif message_type == MessageType.NOTIFICATION_100:
        message = (
            "### GREAT! PROJECT REACHED 100% ###\n"
            + f"Project Name: {project_name}\n"
            + f"Project Id: {project_id}\n\n"
            + "You can set this project to 'finished' "
            + "and activate another one."
        )
        slack_client.chat_postMessage(
            channel="mapswipe_managers", text=message)
    else:
        # TODO: Raise an Exception
        pass


def send_progress_notification(project_id: int):
    """Send progress notification to project managers in Slack."""
    fb_db = auth.firebaseDB()
    progress = fb_db.reference(f"v2/projects/{project_id}/progress").get()

    if not progress:
        logger.info(
            f"could not get progress from firebase for project {project_id}")
    elif progress >= 90:
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
            send_slack_message(MessageType.NOTIFICATION_90,
                               project_name, project_id)
            fb_db.reference(
                f"v2/projects/{project_id}/notification_90_sent").set(True)

        if progress >= 100 and not notification_100_sent:
            # send notification and set value in firebase
            send_slack_message(MessageType.NOTIFICATION_100,
                               project_name, project_id)
            fb_db.reference(
                f"v2/projects/{project_id}/notification_100_sent").set(True)
