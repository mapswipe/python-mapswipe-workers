import json
import sentry_sdk
from sentry_sdk import capture_exception
from mapswipe_workers.definitions import CONFIG_PATH

def init_sentry():

    try:
        with open(CONFIG_PATH) as json_data_file:
            data = json.load(json_data_file)
            sentry_url = data['sentry']['dsn']
            sentry_sdk.init(sentry_url)
            return True
    except:
        print('no sentry config provided')
        return None


def capture_exception_sentry(error):
    capture_exception(error)