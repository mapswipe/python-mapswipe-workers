import json
import csv
from mapswipe_workers.project_types.build_area import tile_functions as t
from mapswipe_workers import auth

# add basic information for tutorial like name, project type, tile server
# load data from examples file
input_file = 'scripts/tutorials/build_area/build_area_tutorial.json'
with open(input_file) as json_file:
    tutorial = json.load(json_file)

print(tutorial)

tutorial_id = tutorial['projectId']

categories = tutorial['categories'].keys()
print(categories)

grouped_tasks = {
    'building_easy': {},
    'building_difficult': {},
    'no_building_easy': {},
    'no_building_difficult': {},
    'bad_clouds': {},
    'bad_no_imagery': {}
}

c=0
with open(tutorial['examplesFile']) as csvDataFile:
    csvReader = csv.reader(csvDataFile)
    for row in csvReader:
        c += 1
        if c==1:
            header = row
        else:
            category = row[2]
            if not row[3] in grouped_tasks[category].keys():
                grouped_tasks[category][row[3]] = {
                    'task_id_list': [],
                    'task_x_list': [],
                    'task_y_list': [],
                    'reference_answer_list': [],
                    'category': category,
                    'url_list': []
                }

            grouped_tasks[category][row[3]]['task_id_list'].append(row[0])
            zoom = row[0].split('-')[0]
            task_x = int(row[0].split('-')[1])
            task_y = int(row[0].split('-')[2])
            grouped_tasks[category][row[3]]['task_x_list'].append(task_x)
            grouped_tasks[category][row[3]]['task_y_list'].append(task_y)
            url = t.tile_coords_zoom_and_tileserver_to_URL(task_x, task_y, zoom, tutorial['tileServer']['name'],
                                                            auth.get_api_key(tutorial['tileServer']['name']), None, None)
            grouped_tasks[category][row[3]]['url_list'].append(url)
            grouped_tasks[category][row[3]]['reference_answer_list'].append(row[1])

groups_dict = {}
tasks_dict = {}

for i in range(0,5):
    print(i)
    group_id = 101 + i
    groups_dict[group_id] = {
        "xMax": "111",
        "xMin": "100",
        "yMax": "202",
        "yMin": "200",
        "requiredCount": 5,
        "finishedCount": 0,
        "groupId": group_id,
        "projectId": tutorial_id,
        "numberOfTasks": 36,
        "progress": 0
    }

    tasks_dict[group_id] = {}
    # select 6 tasks for each category and add to group
    counter = -1
    task_x = 100
    task_y = 200
    for category in categories:
        #print(category)
        keys = list(grouped_tasks[category].keys())
        tasks = grouped_tasks[category][keys[i]]

        x_min = min(tasks['task_x_list'])
        y_min = min(tasks['task_y_list'])


        # replace taskX and TaskY
        # TaskY between 0 and 2
        # TaskX between 0 and 11
        for j in range(0, len(tasks['task_id_list'])):
            counter += 1
            task = {
                'taskId_real': tasks['task_id_list'][j],
                'groupId': group_id,
                'projectId': tutorial_id,
                'referenceAnswer': tasks['reference_answer_list'][j],
                'category': tasks['category'],
                'url': tasks['url_list'][j]
            }

            if tasks['task_x_list'][j] == x_min:
                task['taskX'] = str(task_x)
            elif tasks['task_x_list'][j] == (x_min + 1):
                task['taskX'] = str(task_x + 1)

            if tasks['task_y_list'][j] == y_min:
                task['taskY'] = str(task_y)
            elif tasks['task_y_list'][j] == (y_min + 1):
                task['taskY'] = str(task_y + 1)
            elif tasks['task_y_list'][j] == (y_min + 2):
                task['taskY'] = str(task_y + 2)

            task['taskId'] = '18-{}-{}'.format(task['taskX'], task['taskY'])
            tasks_dict[group_id][counter] = task

        task_x += 2

print(groups_dict)
print(tasks_dict)

# export as json files
with open('scripts/tutorials/build_area/build_area_tutorial_groups.json', 'w') as outfile:
    json.dump(groups_dict, outfile)

with open('scripts/tutorials/build_area/build_area_tutorial_tasks.json', 'w') as outfile:
    json.dump(tasks_dict, outfile)

# upload groups and tasks to firebase
fb_db = auth.firebaseDB()
ref = fb_db.reference('')
ref.update({
    'projects/{}'.format(tutorial_id): tutorial,
    'groups/{}'.format(tutorial_id): groups_dict,
    'tasks/{}'.format(tutorial_id): tasks_dict,
    })







