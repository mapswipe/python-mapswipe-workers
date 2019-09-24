#!/bin/python3
# -*- coding: UTF-8 -*-
# Author: M. Reinmuth, B. Herfort

import sys
import traceback
import json
import slack
from mapswipe_workers.definitions import CONFIG_PATH


def get_slack_client():
    """
    The function to init the slack client from information provided in config file

    Returns
    -------
    sc : slack.WebClient
    channel: str
        name of slack channel
    username : str
        user name for the bot in slack
    """

    try:
        with open(CONFIG_PATH) as json_data_file:
            data = json.load(json_data_file)
            slack_token = data['slack']['token']
            channel = data['slack']['channel']
            username = data['slack']['username']
            sc = slack.WebClient(token=slack_token)
            return sc, channel, username
    except:
        print('no slack token provided')
        return None


def send_slack_message(msg):
    """
    The function to send a message to a slack channel

    Parameters
    ----------
    msg : str
        the message to send as string

    Returns
    -------
    bool
        True if successful, False otherwise
    """

    if not get_slack_client():
        return False
    else:
        sc, channel, username = get_slack_client()
        response = sc.chat_postMessage(
            as_user=True,
            channel=channel,
            text=msg,
            username=username,
            )
        assert response["ok"]
        return True


def _get_error_message_details(error):
    """
    The function to nicely extract error text and traceback."
    Parameters
    ----------
    error : Exception
        the python exception which caused the error
    Returns
    -------
    error_msg_string : str
    """

    type_, value_, traceback_ = sys.exc_info()
    error_msg = traceback.format_exception(type_, value_, traceback_)
    error_msg_string = ''
    for part in error_msg:
        error_msg_string += part + '\n'
    return error_msg_string


def send_error(error):
    """
    The function to send an error message to Slack
    Parameters
    ----------
    error : Exception
        the python exception which caused the error
    Returns
    -------
    bool
        True if successful, false otherwise.
    """

    error_msg = _get_error_message_details(error)
    head = 'python-mapswipe-workers: error occured'
    send_slack_message(head + '\n' + error_msg)
    return True