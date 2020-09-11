import os

from mapswipe_workers.definitions import DATA_PATH, logger, sentry


def create_directories() -> None:
    """Create directories for statistics"""
    dirs = (
        DATA_PATH + "/api",
        DATA_PATH + "/api/agg_results",
        DATA_PATH + "/api/groups",
        DATA_PATH + "/api/history",
        DATA_PATH + "/api/hot_tm",
        DATA_PATH + "/api/projects",
        DATA_PATH + "/api/results",
        DATA_PATH + "/api/tasks",
        DATA_PATH + "/api/yes_maybe",
        DATA_PATH + "/api/users",
        DATA_PATH + "/api/project_geometries",
    )

    for path in dirs:
        if not os.path.exists(path):
            try:
                os.makedirs(path)
            except OSError:
                logger.exception(
                    "Creation of the directory {0} failed".format(path))
                sentry.capture_exception()
                break
            else:
                print("Successfully created the directory {0}".format(path))
