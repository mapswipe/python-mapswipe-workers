import json
import csv
from mapswipe_workers.project_types.build_area import tile_functions as t
from mapswipe_workers import auth

# add basic information for tutorial like name, project type, tile server
# load data from examples file
input_file = 'change_detection_tutorial.json'
with open(input_file) as json_file:
    tutorial = json.load(json_file)

print(tutorial)

tutorial_id = tutorial['projectId']

categories = tutorial['categories'].keys()
print(categories)


grouped_tasks = {
    'changes': {},
    'no_changes': {},
    'maybe': {},
    'bad_imagery': {},
}

# create groups, for each group 6 tiles per category
# make sure to select the tiles that belong to each other
# export groups as json


groups_dict = {}
tasks_dict = {}


with open(tutorial['examplesFile']) as json_file:
    tutorial_tasks = json.load(json_file)
    print(len(tutorial_tasks))
    print(tutorial_tasks)

    for feature in tutorial_tasks['features']:

        print(feature)

        category = feature['properties']['category']
        group_id = 100 + feature['properties']['id']

        if not group_id in groups_dict.keys():
            groups_dict[group_id] = {
                "xMax": "104",
                "xMin": "100",
                "yMax": "200",
                "yMin": "200",
                "requiredCount": 5,
                "finishedCount": 0,
                "groupId": group_id,
                "projectId": tutorial_id,
                "numberOfTasks": 4,
                "progress": 0
            }

        reference = feature['properties']['reference']
        zoom = feature['properties']['TileZ']
        task_x = feature['properties']['TileX']
        task_y = feature['properties']['TileY']
        task_id_real = '{}-{}-{}'.format(zoom, task_x, task_y)

        urlA = t.tile_coords_zoom_and_tileserver_to_URL(
            task_x,
            task_y,
            zoom,
            tutorial['tileServerA']['name'],
            tutorial['tileServerA']['apiKey'],
            tutorial['tileServerA']['url'],
            None,
        )
        urlB = t.tile_coords_zoom_and_tileserver_to_URL(
            task_x,
            task_y,
            zoom,
            tutorial['tileServerB']['name'],
            tutorial['tileServerB']['apiKey'],
            tutorial['tileServerB']['url'],
            None,
        )

        if not group_id in tasks_dict.keys():
            tasks_dict[group_id] = {}
            task_id = '{}-{}-{}'.format(16, 100, 200)
        else:
            task_id = '{}-{}-{}'.format(16, 100 + len(tasks_dict[group_id].keys()), 200)

        task = {
            'taskId_real': task_id_real,
            'taskId': task_id,
            'taskX': 100 + len(tasks_dict[group_id].keys()),
            'taskY': 200,
            'groupId': group_id,
            'projectId': tutorial_id,
            'referenceAnswer': reference,
            'category': category,
            'urlA': urlA,
            'urlB': urlB,
        }

        tasks_dict[group_id][len(tasks_dict[group_id].keys())] = task

print(groups_dict)
print(tasks_dict)


# export as json files
with open('change_detection_tutorial_groups.json', 'w') as outfile:
    json.dump(groups_dict, outfile)

with open('change_detection_tutorial_tasks.json', 'w') as outfile:
    json.dump(tasks_dict, outfile)

# upload groups and tasks to firebase
fb_db = auth.firebaseDB()
ref = fb_db.reference('')
ref.update({
    'v2/projects/{}'.format(tutorial_id): tutorial,
    'v2/groups/{}'.format(tutorial_id): groups_dict,
    'v2/tasks/{}'.format(tutorial_id): tasks_dict,
    })
