import pathlib

from mapswipe_workers.definitions import DATA_PATH


def create_directories() -> None:
    """Create directories"""
    dirs = (
        "/api",
        "/api/agg_results",
        "/api/groups",
        "/api/history",
        "/api/hot_tm",
        "/api/project_geometries",
        "/api/projects",
        "/api/results",
        "/api/tasks",
        "/api/users",
        "/api/yes_maybe",
    )

    for dir_name in dirs:
        path = pathlib.PurePath(DATA_PATH).joinpath(dir_name)
        # mimicking the POSIX mkdir -p command
        path.mkdir(parents=True, exist_ok=True)
