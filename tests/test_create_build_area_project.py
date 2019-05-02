import json
import random
import string
from mapswipe_workers.project_types.build_area.build_area_project \
        import BuildAreaProject


with open('build_area_project_drafts.json') as f:
    sample_project_drafts = json.load(f)

for key in sample_project_drafts.keys():
    project_draft = sample_project_drafts[key]
    # generate random id as string
    project_draft['projectDraftId'] = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
    project = BuildAreaProject(project_draft)
    project.create_groups()

    for group in project.groups:
        print(vars(group))
        for task in group.tasks:
            print(vars(task))
