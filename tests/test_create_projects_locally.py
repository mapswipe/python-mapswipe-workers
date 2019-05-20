import os
import glob
import json

from mapswipe_workers.project_types.build_area.build_area_project \
        import BuildAreaProject
from mapswipe_workers.project_types.footprint.footprint_project \
        import FootprintProject
from mapswipe_workers.project_types.change_detection.change_detection_project \
        import ChangeDetectionProject


def create_project_locally(sample_project_draft):

    project_types = {
            # Make sure to import all project types here
            1: BuildAreaProject,
            2: FootprintProject,
            3: ChangeDetectionProject
            }

    sample_project_type = sample_project_draft.get('projectType', 1)
    sample_project = project_types[sample_project_type](sample_project_draft)
    sample_project.create_groups()
    sample_project.calc_number_of_tasks()


if __name__ == '__main__':
    test_dir = os.path.dirname(os.path.abspath(__file__))
    sample_data_dir = os.path.join(test_dir, 'sample_data/')
    for sample_project_drafts_json in glob.glob(
            sample_data_dir + '*_drafts.json'
            ):
        with open(sample_project_drafts_json) as f:
            sample_project_drafts = json.load(f)
            for key, sample_project_draft in sample_project_drafts.items():
                sample_project_draft['projectDraftId'] = key
                create_project_locally(sample_project_draft)
