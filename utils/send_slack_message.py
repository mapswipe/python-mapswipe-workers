#!/bin/python3
# -*- coding: UTF-8 -*-
# Author: M. Reinmuth, B. Herfort
####################################################################################################
import json

from slackclient import SlackClient


def get_slack_client():
    try:
        with open('../cfg/config.cfg') as json_data_file:
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

