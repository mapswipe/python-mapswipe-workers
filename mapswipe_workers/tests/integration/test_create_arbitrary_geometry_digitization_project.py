import json
import os
import unittest
from unittest.mock import patch

from click.testing import CliRunner

from mapswipe_workers import auth, mapswipe_workers
from mapswipe_workers.definitions import DATA_PATH
from mapswipe_workers.utils.create_directories import create_directories
from tests import fixtures
from tests.fixtures import FIXTURE_DIR
from tests.integration import tear_down


class TestCreateDigitizationProject(unittest.TestCase):
    def setUp(self):
        file_path = os.path.join(FIXTURE_DIR, "projectDrafts", "digitization.json")
        self.project_id = fixtures.create_test_draft(
            file_path, "digitization", "digitization", "projectDrafts"
        )
        create_directories()

    def tearDown(self):
        tear_down.delete_test_data(self.project_id)

    def test_create_digitization_project(self):
        runner = CliRunner()
        with patch(
            "mapswipe_workers.project_types."
            + "arbitrary_geometry.digitization.project.urlretrieve"
        ):
            with open(
                os.path.join(
                    os.path.dirname(os.path.abspath(__file__)),
                    "..",
                    "fixtures",
                    "feature_collection.json",
                ),
                "r",
            ) as file:
                output_file_path = (
                    f"{DATA_PATH}/input_geometries/"
                    + f"raw_input_{self.project_id}.geojson"
                )
                with open(output_file_path, "w") as out_file:
                    json.dump(json.load(file), out_file)

            result = runner.invoke(
                mapswipe_workers.run_create_projects, catch_exceptions=False
            )
        if result.exit_code != 0:
            raise result.exception
        pg_db = auth.postgresDB()

        query = """
            SELECT project_id, project_type_specifics
            FROM projects
            WHERE project_id = %s
        """
        result = pg_db.retr_query(query, [self.project_id])[0]
        self.assertEqual(result[0], self.project_id)

        self.assertEqual(result[1]["tileServer"]["maxZoom"], 18)

        query = "SELECT count(*) FROM groups WHERE project_id = %s"
        result = pg_db.retr_query(query, [self.project_id])[0][0]
        self.assertEqual(result, 1)

        query = "SELECT number_of_tasks FROM groups WHERE project_id = %s"
        result = pg_db.retr_query(query, [self.project_id])[0][0]
        self.assertEqual(result, 1)

        query = "SELECT count(*) FROM tasks WHERE project_id = %s"
        result = pg_db.retr_query(query, [self.project_id])[0][0]
        self.assertEqual(result, 1)

        fb_db = auth.firebaseDB()
        ref = fb_db.reference(f"/v2/projects/{self.project_id}")
        result = ref.get(shallow=True)
        self.assertIsNotNone(result)

        ref = fb_db.reference(f"/v2/groups/{self.project_id}")
        result = ref.get(shallow=True)
        self.assertIsNotNone(result)

        # digitization projects have tasks in Firebase
        ref = fb_db.reference(f"/v2/tasks/{self.project_id}")
        result = ref.get(shallow=True)
        self.assertIsNotNone(result)


if __name__ == "__main__":
    unittest.main()
