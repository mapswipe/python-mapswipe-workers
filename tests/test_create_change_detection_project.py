import json
import random
import string
from mapswipe_workers.project_types.change_detection.change_detection_project \
        import ChangeDetectionProject


input_file = 'change_detection_project_drafts.json'
output_file = 'change_detection_project_{}_{}.json'
with open(input_file) as f:
    sample_project_drafts = json.load(f)

for key in sample_project_drafts.keys():
    project_draft = sample_project_drafts[key]
    # generate random id as string
    project_draft['projectDraftId'] = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
    project = ChangeDetectionProject(project_draft)
    project.create_groups()

    for group in project.groups:
        group.requiredCount = project.verificationNumber
        project.numberOfTasks = (
                project.numberOfTasks +
                group.requiredCount *
                group.numberOfTasks
        )

    # Convert object attributes to dictonaries
    # for saving it to firebase and postgres
    project_dict = vars(project)
    groups = dict()
    groupsOfTasks = dict()
    for group in project.groups:
        group = vars(group)
        tasks = list()
        for task in group['tasks']:
            tasks.append(vars(task))
        groupsOfTasks[group['groupId']] = tasks
        del group['tasks']
        groups[group['groupId']] = group
    del (project_dict['groups'])
    project_dict.pop('inputGeometries', None)
    project_dict.pop('kml', None)
    project_dict.pop('validInputGeometries', None)


    with open(output_file.format(project.projectId, 'groups'), 'w') as outfile:
        json.dump(groups, outfile)

    with open(output_file.format(project.projectId, 'tasks'), 'w') as outfile:
        json.dump(groupsOfTasks, outfile)
