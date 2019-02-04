#!/bin/python3
# -*- coding: UTF-8 -*-
# Author: M. Reinmuth, B. Herfort
####################################################################################################
import json
from mapswipe_workers import definitions
from slackclient import SlackClient

def get_slack_client():
    """
    The function to init the slack client from information provided in config file

    Returns
    -------
    sc : SlackClient
    channel: str
        name of slack channel
    username : str
        user name for the bot in slack
    """

    try:
        with open(definitions.CONFIG_PATH) as json_data_file:
            data = json.load(json_data_file)
            slack_token = data['slack']['token']
            channel = data['slack']['channel']
            username = data['slack']['username']
            sc = SlackClient(slack_token)
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

        sc.api_call(
            "chat.postMessage",
            channel=channel,
            text=msg,
            username=username
        )
        print('sent slack message.')
        return True


####################################################################################################
if __name__ == '__main__':

    head = 'Test slack api python integration:'
    message = 'Hello world!'
    send_slack_message(head + '\n' + message)

