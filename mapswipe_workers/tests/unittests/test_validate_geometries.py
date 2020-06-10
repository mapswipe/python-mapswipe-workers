import os
import json
import unittest
from mapswipe_workers.definitions import ProjectType


class TestUserStats(unittest.TestCase):
    def setUp(self):
        test_dir = os.path.dirname(os.path.abspath(__file__))
        with open(
            os.path.join(test_dir, "fixtures/completeness/projectDraft.json")
        ) as json_file:
            project_draft = json.load(json_file)
            self.project_type = project_draft["projectType"]
            self.project = ProjectType(self.project_type).constructor(project_draft)


if __name__ == "__main__":
    unittest.main()
