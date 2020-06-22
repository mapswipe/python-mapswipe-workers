import os
import unittest
import json
import pickle
from mapswipe_workers.definitions import ProjectType


class TestCreateTutorialBuildArea(unittest.TestCase):
    def setUp(self) -> None:

        test_dir = os.path.dirname(__file__)
        data_dir = os.path.join(test_dir, "fixtures", "tile_map_service_grid")
        tutorial_file = os.path.join(
            data_dir, "tutorials", "change_detection_tutorial_kutupalong.json"
        )

        with open(tutorial_file) as json_file:
            self.tutorial_draft = json.load(json_file)

    def test_create_tutorial(self):

        project_type = self.tutorial_draft["projectType"]
        tutorial = ProjectType(project_type).tutorial(self.tutorial_draft)

        test_dir = os.path.dirname(__file__)
        data_dir = os.path.join(test_dir, "fixtures", "tile_map_service_grid")
        project_file = os.path.join(
            data_dir, "projects", "change_detection_tutorial_kutupalong_project.pickle"
        )

        with open(project_file, "rb") as handle:
            tutorial_project_exp = pickle.load(handle)

        self.assertDictEqual(vars(tutorial), vars(tutorial_project_exp))

    def test_create_tutorial_groups(self):
        project_type = self.tutorial_draft["projectType"]
        tutorial = ProjectType(project_type).tutorial(self.tutorial_draft)
        tutorial.create_tutorial_groups()

        test_dir = os.path.dirname(__file__)
        data_dir = os.path.join(test_dir, "fixtures", "tile_map_service_grid")
        groups_file = os.path.join(
            data_dir,
            "groups",
            "change_detection_tutorial_kutupalong_project_groups.pickle",
        )

        with open(groups_file, "rb") as handle:
            groups_exp = pickle.load(handle)

        self.assertDictEqual(tutorial.groups, groups_exp)

    def test_create_tutorial_tasks(self):
        project_type = self.tutorial_draft["projectType"]
        tutorial = ProjectType(project_type).tutorial(self.tutorial_draft)
        tutorial.create_tutorial_groups()
        tutorial.create_tutorial_tasks()

        test_dir = os.path.dirname(__file__)
        data_dir = os.path.join(test_dir, "fixtures", "tile_map_service_grid")
        tasks_file = os.path.join(
            data_dir,
            "tasks",
            "change_detection_tutorial_kutupalong_project_tasks.pickle",
        )

        with open(tasks_file, "rb") as handle:
            tasks_exp = pickle.load(handle)

        self.assertDictEqual(tutorial.tasks, tasks_exp)


if __name__ == "__main__":
    unittest.main()
