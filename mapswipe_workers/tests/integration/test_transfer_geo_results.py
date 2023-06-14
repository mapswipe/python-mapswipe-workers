import json
import os
import unittest
from unittest.mock import patch

from click.testing import CliRunner

from mapswipe_workers import auth, mapswipe_workers
from mapswipe_workers.definitions import DATA_PATH, logger
from mapswipe_workers.firebase_to_postgres.transfer_results import transfer_results
from mapswipe_workers.utils.create_directories import create_directories
from tests import fixtures
from tests.fixtures import FIXTURE_DIR
from tests.integration import set_up, tear_down
from tests.integration.base import BaseTestCase


class TestTransferGeoResultsProject(BaseTestCase):
    def setUp(self):
        super().setUp()
        file_path = os.path.join(FIXTURE_DIR, "projectDrafts", "digitization.json")
        self.project_id = fixtures.create_test_draft(
            file_path, "digitization", "digitization", "projectDrafts"
        )
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

            runner.invoke(mapswipe_workers.run_create_projects, catch_exceptions=False)

        set_up.set_firebase_test_data(
            "digitization", "results", "digitization", self.project_id
        )
        create_directories()

    def tearDown(self):
        tear_down.delete_test_data(self.project_id)

    def verify_mapping_results_in_postgres(self):
        """Check that mapping_sessions and mapping_sessions_results
        contain the expected data.
        """
        pg_db = auth.postgresDB()
        expected_items_count = 1

        sql_query = (
            f"SELECT * "
            f"FROM mapping_sessions "
            f"WHERE project_id = '{self.project_id}' "
            f"AND user_id = '{self.project_id}'"
        )
        result = pg_db.retr_query(sql_query)
        self.assertEqual(len(result), 1)
        logger.info(result)
        self.assertEqual(expected_items_count, result[0][6])

        q2 = (
            "SELECT msr.*"
            "FROM mapping_sessions_results_geometry msr "
            "JOIN mapping_sessions ms ON "
            "ms.mapping_session_id = msr.mapping_session_id "
            f"WHERE ms.project_id = '{self.project_id}' "
            f"AND ms.user_id = '{self.project_id}'"
        )
        result2 = pg_db.retr_query(q2)
        self.assertEqual(len(result2), expected_items_count)

    def test_changes_given_project_id(self):
        """Test if results are deleted from Firebase for given project id."""

        transfer_results(project_id_list=[self.project_id])

        fb_db = auth.firebaseDB()
        ref = fb_db.reference("v2/results/{0}".format(self.project_id))
        self.assertIsNone(ref.get())

        self.verify_mapping_results_in_postgres()

    def test_changes_given_no_project_id(self):
        """Test if results are deleted from Firebase with no given project id."""
        transfer_results()

        fb_db = auth.firebaseDB()
        ref = fb_db.reference("v2/results/{0}".format(self.project_id))
        self.assertIsNone(ref.get())
        self.verify_mapping_results_in_postgres()

    def test_user_not_in_postgres(self):
        """Test if results are transferred for users which are not yet in Postgres."""
        pg_db = auth.postgresDB()

        # Make sure user and results are not yet in Postgres
        sql_query = (
            f"DELETE FROM mapping_sessions "
            f"WHERE user_id = '{self.project_id}' "
            f"AND project_id = '{self.project_id}'"
        )
        pg_db.query(sql_query)
        sql_query = "DELETE FROM users WHERE user_id = '{0}'".format(self.project_id)
        pg_db.query(sql_query)

        transfer_results()

        sql_query = "SELECT user_id FROM users WHERE user_id = '{0}'".format(
            self.project_id
        )
        result = pg_db.retr_query(sql_query)
        self.assertEqual(len(result), 1)
        # FIXME: the name is misleading here, it is the user_id
        self.assertEqual(result[0][0], self.project_id)

        sql_query = (
            "SELECT * "
            "FROM mapping_sessions "
            f"WHERE project_id = '{self.project_id}' "
            f"AND user_id = '{self.project_id}'"
        )
        result = pg_db.retr_query(sql_query)
        self.assertEqual(len(result), 1)


if __name__ == "__main__":
    unittest.main()
