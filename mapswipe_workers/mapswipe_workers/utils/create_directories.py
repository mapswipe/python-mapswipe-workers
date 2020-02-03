import os

from mapswipe_workers.definitions import DATA_PATH, logger, sentry


def create_directories() -> None:
    """Create directories for statistics"""
    dirs = (
        DATA_PATH + "api-data",
        DATA_PATH + "api-data/agg_results",
        DATA_PATH + "api-data/groups",
        DATA_PATH + "api-data/history",
        DATA_PATH + "api-data/hot_tm",
        DATA_PATH + "api-data/projects",
        DATA_PATH + "api-data/results",
        DATA_PATH + "api-data/tasks",
        DATA_PATH + "api-data/yes_maybe",
    )

    for path in dirs:
        if not os.path.exists(path):
            try:
                os.makedirs(path)
            except OSError:
                logger.exception("Creation of the directory {0} failed".format(path))
                sentry.capture_exception()
                break
            else:
                print("Successfully created the directory {0}".format(path))
