"""Error handling utils."""
import sys
import traceback
from mapswipe_workers.utils import slack


def _get_error_message_details(error):
    """Nicely extract error text and traceback."""
    type_, value_, traceback_ = sys.exc_info()
    error_msg = traceback.format_exception(type_, value_, traceback_)
    error_msg_string = ''
    for part in error_msg:
        error_msg_string += part + '\n'
    return error_msg_string


def send_error(error, process):
    """Send error message to logger and Slack."""
    error_msg = _get_error_message_details(error)
    head = 'python-mapswipe-workers: error occured during "{}"'.format(process)
    slack.send_slack_message(head + '\n' + error_msg)
