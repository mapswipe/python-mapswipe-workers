import unittest

import set_up
import tear_down

from mapswipe_workers import auth, mapswipe_workers
from mapswipe_workers.utils.create_directories import create_directories


class TestCreateProject(unittest.TestCase):
    def setUp(self):
        self.project_id = [
            set_up.create_test_project_draft("footprint", "footprint_aoiFile"),
            set_up.create_test_project_draft("footprint", "footprint_link"),
            set_up.create_test_project_draft("footprint", "footprint_TMId"),
        ]
        create_directories()

    def tearDown(self):
        for element in self.project_id:
            tear_down.delete_test_data(element)

    def test_create_footprint_project(self):
        mapswipe_workers.run_create_projects()
        pg_db = auth.postgresDB()
        for element in self.project_id:
            query = "SELECT project_id FROM projects WHERE project_id = %s"
            result = pg_db.retr_query(query, [element])[0][0]
            self.assertEqual(result, element)
            fb_db = auth.firebaseDB()
            ref = fb_db.reference(f"/v2/projects/{element}")
            result = ref.get(shallow=True)
            self.assertIsNotNone(result)

            ref = fb_db.reference(f"/v2/groups/{element}")
            result = ref.get(shallow=True)
            self.assertIsNotNone(result)

            # Footprint projects have tasks in Firebase
            ref = fb_db.reference(f"/v2/tasks/{element}")
            result = ref.get(shallow=True)
            self.assertIsNotNone(result)


if __name__ == "__main__":
    unittest.main()
