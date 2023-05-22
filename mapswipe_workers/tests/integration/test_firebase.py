import json
import os
import unittest

from mapswipe_workers.firebase.firebase import Firebase
from tests.integration import tear_down


class TestFirebase(unittest.TestCase):
    def setUp(self):
        self.firebase = Firebase()
        self.ids = []

    def tearDown(self):
        for id in self.ids:
            tear_down.delete_test_data(id)

    def test_project_to_firebase(self):
        path = "./fixtures/tile_map_service_grid/projects/build_area_with_geometry.json"
        test_dir = os.path.dirname(os.path.abspath(__file__))
        with open(os.path.join(test_dir, path)) as json_file:
            project = json.load(json_file)
        self.ids.append(project["projectId"])
        self.firebase.save_project_to_firebase(project)

        self.firebase.ref = self.firebase.fb_db.reference(
            f"/v2/projects/{project['projectId']}"
        )
        result = self.firebase.ref.get(shallow=True)
        self.assertIsNotNone(result)
        self.assertNotIn("geometry", result)

    def test_groups_to_firebase(self):
        path = "./fixtures/tile_map_service_grid/groups/build_area.json"
        test_dir = os.path.dirname(os.path.abspath(__file__))
        with open(os.path.join(test_dir, path)) as json_file:
            groups = json.load(json_file)
        project_id = groups["g101"]["projectId"]
        self.ids.append(project_id)
        self.firebase.save_groups_to_firebase(project_id, groups)

        self.firebase.ref = self.firebase.fb_db.reference(f"/v2/groups/{project_id}")
        result = self.firebase.ref.get(shallow=True)
        self.assertIsNotNone(result)

    def test_tasks_to_firebase_with_compression(self):
        path = "./fixtures/tile_map_service_grid/tasks/build_area.json"
        test_dir = os.path.dirname(os.path.abspath(__file__))
        with open(os.path.join(test_dir, path)) as json_file:
            tasks = json.load(json_file)
        project_id = tasks["g101"][0]["projectId"]
        self.ids.append(project_id)
        self.firebase.save_tasks_to_firebase(project_id, tasks, useCompression=True)
        self.firebase.ref = self.firebase.fb_db.reference(f"/v2/tasks/{project_id}")
        result = self.firebase.ref.get()
        self.assertIsNotNone(result)
        self.assertNotIsInstance(result["g101"], list)

    def test_tasks_to_firebase_without_compression(self):
        path = "./fixtures/tile_map_service_grid/tasks/build_area.json"
        test_dir = os.path.dirname(os.path.abspath(__file__))
        with open(os.path.join(test_dir, path)) as json_file:
            tasks = json.load(json_file)
        project_id = tasks["g101"][0]["projectId"]
        self.ids.append(project_id)
        self.firebase.save_tasks_to_firebase(project_id, tasks, useCompression=False)
        self.firebase.ref = self.firebase.fb_db.reference(f"/v2/tasks/{project_id}")
        result = self.firebase.ref.get()
        self.assertIsNotNone(result)
        self.assertIsInstance(result["g101"], list)


if __name__ == "__main__":
    unittest.main()
