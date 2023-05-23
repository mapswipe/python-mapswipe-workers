import unittest

from click.testing import CliRunner

from mapswipe_workers import auth, mapswipe_workers
from mapswipe_workers.utils.create_directories import create_directories

from . import set_up, tear_down


def setUpProjectDraft(project_type_name, file_name):
    project_id = set_up.create_test_project_draft(project_type_name, file_name)
    create_directories()
    return project_id


class TestCreateTileClassificationProject(unittest.TestCase):
    def tearDown(self):
        tear_down.delete_test_data(self.project_id)

    def test_create_project_with_additional_attributes(self):
        self.project_id = setUpProjectDraft(
            "tile_classification", "tile_classification_with_additional_attributes"
        )
        runner = CliRunner()
        runner.invoke(mapswipe_workers.run_create_projects)

        pg_db = auth.postgresDB()
        query = """
            SELECT project_type_specifics -> 'language'
            FROM projects WHERE project_id = %s
        """
        result = pg_db.retr_query(query, [self.project_id])[0][0]
        self.assertEqual(result, "de-de")

        query = """
            SELECT project_type_specifics -> 'appId'
            FROM projects WHERE project_id = %s
        """
        result = pg_db.retr_query(query, [self.project_id])[0][0]
        self.assertEqual(result, 99)

        query = """
            SELECT project_type_specifics -> 'manualUrl'
            FROM projects WHERE project_id = %s
        """
        result = pg_db.retr_query(query, [self.project_id])[0][0]
        self.assertEqual(result, "https://www.mapswipe.org")

        fb_db = auth.firebaseDB()
        ref = fb_db.reference(f"/v2/projects/{self.project_id}/language")
        result = ref.get(shallow=True)
        self.assertEqual(result, "de-de")

        ref = fb_db.reference(f"/v2/projects/{self.project_id}/appId")
        result = ref.get(shallow=True)
        self.assertEqual(result, 99)

        ref = fb_db.reference(f"/v2/projects/{self.project_id}/manualUrl")
        result = ref.get(shallow=True)
        self.assertEqual(result, "https://www.mapswipe.org")

    def test_create_project_with_default_attributes(self):
        """
        default values are 'en-us' for language
        and None for appId and manualUrl
        """
        self.project_id = setUpProjectDraft(
            "tile_classification", "tile_classification"
        )
        runner = CliRunner()
        runner.invoke(mapswipe_workers.run_create_projects)

        pg_db = auth.postgresDB()
        query = """
            SELECT project_type_specifics -> 'language'
            FROM projects WHERE project_id = %s
        """
        result = pg_db.retr_query(query, [self.project_id])[0][0]
        self.assertEqual(result, "en-us")

        query = """
            SELECT project_type_specifics -> 'appId'
            FROM projects WHERE project_id = %s
        """
        result = pg_db.retr_query(query, [self.project_id])[0][0]
        self.assertIsNone(result)

        query = """
            SELECT project_type_specifics -> 'manualUrl'
            FROM projects WHERE project_id = %s
        """
        result = pg_db.retr_query(query, [self.project_id])[0][0]
        self.assertIsNone(result)

        fb_db = auth.firebaseDB()
        ref = fb_db.reference(f"/v2/projects/{self.project_id}/language")
        result = ref.get(shallow=True)
        self.assertEqual(result, "en-us")

        ref = fb_db.reference(f"/v2/projects/{self.project_id}/appId")
        result = ref.get(shallow=True)
        self.assertIsNone(result)

        ref = fb_db.reference(f"/v2/projects/{self.project_id}/manualUrl")
        result = ref.get(shallow=True)
        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
