import csv

from mapswipe_workers.definitions import logger
from mapswipe_workers import auth
from mapswipe_workers.utils import tile_functions as t


def create_tutorial(tutorial):
    tutorial, groups_dict, tasks_dict = generate_tutorial_data(tutorial)
    upload_tutorial_to_firebase(tutorial, groups_dict, tasks_dict)


def generate_tutorial_data(tutorial):
    tutorial_id = tutorial["projectId"]
    categories = tutorial["categories"].keys()
    logger.info(f"create tutorial for tutorial id: {tutorial_id}")

    grouped_tasks = {
        "building_easy_1": {},
        "building_easy_2": {},
        "maybe_1": {},
        "no_building_easy_1": {},
        "no_building_easy_2": {},
        "bad_clouds_1": {},
        "bad_no_imagery_1": {},
        "bad_no_imagery_2": {},
    }

    c = 0
    with open(tutorial["examplesFile"]) as csvDataFile:
        logger.info(f'tutorial tasks are based on: {tutorial["examplesFile"]}')
        csvReader = csv.reader(csvDataFile)
        for row in csvReader:
            c += 1
            if c == 1:
                pass
            else:
                category = row[2]
                if not row[3] in grouped_tasks[category].keys():
                    grouped_tasks[category][row[3]] = {
                        "task_id_list": [],
                        "task_x_list": [],
                        "task_y_list": [],
                        "reference_answer_list": [],
                        "category": category,
                        "url_list": [],
                    }

                grouped_tasks[category][row[3]]["task_id_list"].append(row[0])
                zoom = row[0].split("-")[0]
                task_x = int(row[0].split("-")[1])
                task_y = int(row[0].split("-")[2])
                grouped_tasks[category][row[3]]["task_x_list"].append(task_x)
                grouped_tasks[category][row[3]]["task_y_list"].append(task_y)
                url = t.tile_coords_zoom_and_tileserver_to_URL(
                    task_x,
                    task_y,
                    zoom,
                    tutorial["tileServer"]["name"],
                    auth.get_api_key(tutorial["tileServer"]["name"]),
                    None,
                    None,
                )
                grouped_tasks[category][row[3]]["url_list"].append(url)
                grouped_tasks[category][row[3]]["reference_answer_list"].append(row[1])

    groups_dict = {}
    tasks_dict = {}

    for i in range(0, 1):
        group_id = 101 + i
        # the yMin represents a tile located at the equator at zoom level 18
        groups_dict[group_id] = {
            "xMax": "115",
            "xMin": "100",
            "yMax": "131074",
            "yMin": "131072",
            "requiredCount": 5,
            "finishedCount": 0,
            "groupId": group_id,
            "projectId": tutorial_id,
            "numberOfTasks": 36,
            "progress": 0,
        }

        tasks_dict[group_id] = {}
        # select 6 tasks for each category and add to group
        counter = -1
        task_x = 100
        # the task_y represents a tile located at the equator at zoom level 18
        task_y = 131072
        for category in categories:
            # print(category)
            keys = list(grouped_tasks[category].keys())
            tasks = grouped_tasks[category][keys[i]]

            x_min = min(tasks["task_x_list"])
            y_min = min(tasks["task_y_list"])

            # replace taskX and TaskY
            # TaskY between 0 and 2
            # TaskX between 0 and 11
            for j in range(0, len(tasks["task_id_list"])):
                counter += 1
                task = {
                    "taskId_real": tasks["task_id_list"][j],
                    "groupId": group_id,
                    "projectId": tutorial_id,
                    "referenceAnswer": tasks["reference_answer_list"][j],
                    "category": tasks["category"],
                    "url": tasks["url_list"][j],
                }

                if tasks["task_x_list"][j] == x_min:
                    task["taskX"] = str(task_x)
                elif tasks["task_x_list"][j] == (x_min + 1):
                    task["taskX"] = str(task_x + 1)

                if tasks["task_y_list"][j] == y_min:
                    task["taskY"] = str(task_y)
                elif tasks["task_y_list"][j] == (y_min + 1):
                    task["taskY"] = str(task_y + 1)
                elif tasks["task_y_list"][j] == (y_min + 2):
                    task["taskY"] = str(task_y + 2)

                task["taskId"] = "18-{}-{}".format(task["taskX"], task["taskY"])
                tasks_dict[group_id][counter] = task

            task_x += 2

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
