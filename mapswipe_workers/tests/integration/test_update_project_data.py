import unittest

from mapswipe_workers.firebase_to_postgres import update_data


class TestUpdateProjectData(unittest.TestCase):
    def setUp(self):
        self.project_ids = [
            "-MRuCvru6yfFrJZxWn_z",
            "-MOXET8nkuvw2AqGpQDQ",
            "-MCGa66fcuFS6fi9M8-M",
        ]

    def test_custom_project_ids(self):
        """Test update users when no users are in postgres yet."""
        update_data.update_project_data(self.project_ids)
        # self.assertIsNotNone(result)

    def test_non_archived_projects(self):
        """Test update users when no users are in postgres yet."""
        update_data.update_project_data()
        # self.assertIsNotNone(result)


if __name__ == "__main__":
    unittest.main()
