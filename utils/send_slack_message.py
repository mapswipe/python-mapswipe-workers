#!/bin/python3
# -*- coding: UTF-8 -*-
# Author: M. Reinmuth, B. Herfort
########################################################################################################################

from slackclient import SlackClient
import json


def get_slack_client():
    try:
        with open('../cfg/config.cfg') as json_data_file:
            data = json.load(json_data_file)
            slack_token = data['slack']['token']
            channel = data['slack']['channel']
            sc = SlackClient(slack_token)
            return sc, channel
    except:
        print('no slack token provided')
        return None


def send_slack_message(msg):

    if not get_slack_client():
        return False
    else:
        sc, channel = get_slack_client()

        sc.api_call(
            "chat.postMessage",
            channel=channel,
            text=msg
            )
        print('sent slack message.')
        return True


########################################################################################################################
if __name__ == '__main__':

    head = 'Test slack api python integration:'
    message = 'Hello world!'

    send_slack_message(head + '\n' + message)

