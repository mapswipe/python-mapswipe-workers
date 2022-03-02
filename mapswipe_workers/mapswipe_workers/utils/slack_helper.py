from typing import Optional

import slack

from mapswipe_workers import auth
from mapswipe_workers.config import SLACK_CHANNEL, SLACK_TOKEN
from mapswipe_workers.definitions import MessageType, logger


def send_slack_message(
    message_type: MessageType,
    project_name: str,
    project_id: Optional[str],
    details: str = "no details provided",
):
    """Initialize slack client with values provided in environment."""
    if SLACK_TOKEN in [None, ""] or SLACK_CHANNEL in [None, ""]:
        logger.info(
            "No configuration for Slack was found. "
            + f"No '{message_type}' Slack message was sent."
        )
        return None

    slack_client = slack.WebClient(token=SLACK_TOKEN)

    if message_type == MessageType.SUCCESS:
        message = (
            "### PROJECT CREATION SUCCESSFUL ###\n"
            + f"Project Name: {project_name}\n"
            + f"Project Id: {project_id}\n\n"
            + "Make sure to activate the project using the manager dashboard.\n"
            + "Happy Swiping. :)"
        )
        slack_client.chat_postMessage(channel=SLACK_CHANNEL, text=message)
    elif message_type == MessageType.FAIL:
        message = (
            "### PROJECT CREATION FAILED ###\n"
            + f"Project Name: {project_name}\n"
            + "Project draft is deleted.\n\n"
            + "REASON:\n"
            + f"{details}"
        )
        slack_client.chat_postMessage(channel=SLACK_CHANNEL, text=message)
    elif message_type == MessageType.NOTIFICATION_90:
        message = (
            "### ALMOST THERE! PROJECT REACHED 90% ###\n"
            + f"Project Name: {project_name}\n"
            + f"Project Id: {project_id}\n\n"
            + "Get your next projects ready."
        )
        slack_client.chat_postMessage(channel="mapswipe_managers", text=message)
    elif message_type == MessageType.NOTIFICATION_100:
        message = (
            "### GREAT! PROJECT REACHED 100% ###\n"
            + f"Project Name: {project_name}\n"
            + f"Project Id: {project_id}\n\n"
            + "You can set this project to 'finished' "
            + "and activate another one."
        )
        slack_client.chat_postMessage(channel="mapswipe_managers", text=message)
    elif message_type == MessageType.PROJECT_STATUS_FINISHED:
        message = (
            "### SET PROJECT STATUS TO FINISHED ###\n"
            + f"Project Name: {project_name}\n"
            + f"Project Id: {project_id}\n\n"
            + "The status of the project has been set to 'finished' "
            + "by MapSwipe's backend workers."
        )
        slack_client.chat_postMessage(channel=SLACK_CHANNEL, text=message)
    elif message_type == MessageType.PROJECT_STATUS_ACTIVE:
        message = (
            "### SET PROJECT STATUS TO ACTIVE ###\n"
            + f"Project Name: {project_name}\n"
            + f"Project Id: {project_id}\n\n"
            + "The status of the project has been set to 'active' "
            + "by MapSwipe's backend workers."
        )
        slack_client.chat_postMessage(channel=SLACK_CHANNEL, text=message)
    else:
        # TODO: Raise an Exception
        pass


def send_progress_notification(project_id: str):
    """Send progress notification to project managers in Slack."""
    fb_db = auth.firebaseDB()
    progress = fb_db.reference(f"v2/projects/{project_id}/progress").get()

    if not progress:
        logger.info(f"could not get progress from firebase for project {project_id}")
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
            send_slack_message(MessageType.NOTIFICATION_90, project_name, project_id)
            fb_db.reference(f"v2/projects/{project_id}/notification_90_sent").set(True)

        if progress >= 100 and not notification_100_sent:
            # send notification and set value in firebase
            send_slack_message(MessageType.NOTIFICATION_100, project_name, project_id)
            fb_db.reference(f"v2/projects/{project_id}/notification_100_sent").set(True)
