from mapswipe_workers.utils import sentry
from mapswipe_workers.utils import slack

sentry.init_sentry()

try:
    division_by_zero = 1 / 0
except Exception as e:
    # Alternatively the argument can be omitted
    sentry.capture_exception_sentry(e)
    slack.send_error(e)




