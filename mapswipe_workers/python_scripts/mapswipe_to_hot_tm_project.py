import json
from mapswipe_workers.definitions import DATA_PATH


def mapswipe_to_hot_tm_project(project_id, project_name):

    # get project aoi
    aoi_file = f"{DATA_PATH}/api/project_geometries/project_geom_{project_id}.geojson"
    with open(aoi_file) as f:
        aoi_geojson = json.load(f)

    # get tasks
    tasks_file = f"{DATA_PATH}/api/hot_tm/hot_tm_{project_id}.geojson"
    with open(tasks_file) as f:
        tasks_geojson = json.load(f)

    data = {
        "arbitraryTasks": True,
        "areaOfInterest": aoi_geojson,
        "projectName": project_name,
        "tasks": tasks_geojson,
    }

    print(data)


mapswipe_project_id = "build_area_default_with_bing"
tm_project_name = "benni_test"
mapswipe_to_hot_tm_project(mapswipe_project_id, tm_project_name)
