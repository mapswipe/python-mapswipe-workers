import json
from mapswipe_workers.definitions import logger
from mapswipe_workers import auth
from mapswipe_workers.utils import tile_functions as t


def create_tutorial(tutorial):
    tutorial, groups_dict, tasks_dict = generate_tutorial_data(tutorial)
    upload_tutorial_to_firebase(tutorial, groups_dict, tasks_dict)


def generate_tutorial_data(tutorial):
    tutorial_id = tutorial["projectId"]
    logger.info(f"create tutorial for tutorial id: {tutorial_id}")

    groups_dict = {}
    tasks_dict = {}

    with open(tutorial["examplesFile"]) as json_file:
        tutorial_tasks = json.load(json_file)

        for feature in tutorial_tasks["features"]:
            category = feature["properties"]["category"]
            group_id = 100 + feature["properties"]["id"]

            if group_id not in groups_dict.keys():

                # yMin 32768 represents a tile located at the equator at zoom level 16
                groups_dict[group_id] = {
                    "xMax": "105",
                    "xMin": "100",
                    "yMax": "32768",
                    "yMin": "32768",
                    "requiredCount": 5,
                    "finishedCount": 0,
                    "groupId": group_id,
                    "projectId": tutorial_id,
                    "numberOfTasks": 4,
                    "progress": 0,
                }

            reference = feature["properties"]["reference"]
            zoom = feature["properties"]["TileZ"]
            task_x = feature["properties"]["TileX"]
            task_y = feature["properties"]["TileY"]
            task_id_real = "{}-{}-{}".format(zoom, task_x, task_y)

            urlA = t.tile_coords_zoom_and_tileserver_to_url(
                task_x, task_y, zoom, tutorial["tileServerA"]
            )
            urlB = t.tile_coords_zoom_and_tileserver_to_url(
                task_x, task_y, zoom, tutorial["tileServerB"]
            )

            if group_id not in tasks_dict.keys():
                tasks_dict[group_id] = {}
                task_id = "{}-{}-{}".format(16, 100, 32768)
            else:
                task_id = "{}-{}-{}".format(
                    16, 100 + len(tasks_dict[group_id].keys()), 32768
                )

            task = {
                "taskId_real": task_id_real,
                "taskId": task_id,
                "taskX": 100 + len(tasks_dict[group_id].keys()),
                "taskY": 32768,
                "groupId": group_id,
                "projectId": tutorial_id,
                "referenceAnswer": reference,
                "category": category,
                "urlA": urlA,
                "urlB": urlB,
            }

            tasks_dict[group_id][len(tasks_dict[group_id].keys())] = task

    return tutorial, groups_dict, tasks_dict


def upload_tutorial_to_firebase(tutorial, groups_dict, tasks_dict):
    # upload groups and tasks to firebase
    tutorial_id = tutorial["projectId"]

    fb_db = auth.firebaseDB()
    ref = fb_db.reference("")
    ref.update(
        {
            "v2/projects/{}".format(tutorial_id): tutorial,
            "v2/groups/{}".format(tutorial_id): groups_dict,
            "v2/tasks/{}".format(tutorial_id): tasks_dict,
        }
    )
    logger.info(f"uploaded tutorial data to firebase for {tutorial_id}")
