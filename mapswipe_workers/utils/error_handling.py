import sys
import traceback
from mapswipe_workers.utils import slack


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


def send_error(error, process):
    """
    The function to send an error message to Slack

    Parameters
    ----------
    error : Exception
        the python exception which caused the error

    process : str
        the name of the process for which the exception occurred, e.g. 'import'

    Returns
    -------
    bool
        True if successful, false otherwise.
    """

    error_msg = _get_error_message_details(error)
    head = 'python-mapswipe-workers: error occured during "{}"'.format(process)
    slack.send_slack_message(head + '\n' + error_msg)
    return True

def log_error(error, logger):
    """
    The function to log error to logging file

    Parameters
    ----------
    error : Exception
        the python exception which caused the error
    logger : logging.logger
        the logger object

    Returns
    -------
    bool
        True if successful, false otherwise.
    """

    error_msg = _get_error_message_details(error)
    logger.error('Error detail:\n' + error_msg)
    return True
