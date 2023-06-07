import json
import os
import unittest

from mapswipe_workers import auth
from mapswipe_workers.firebase_to_postgres.transfer_results import (
    transfer_results,
    transfer_results_for_project,
)
from tests.integration import set_up, tear_down

from .base import BaseTestCase


class TestTransferResultsProject(BaseTestCase):
    def setUp(self):
        super().setUp()
        project_type = "tile_map_service_grid"
        fixture_name = "build_area"
        self.project_id = set_up.create_test_project(
            project_type, fixture_name, results=False
        )
        # add some results in firebase
        set_up.set_firebase_test_data(project_type, "users", "user", self.project_id)
        set_up.set_firebase_test_data(project_type, "userGroups", "user_group", "")
        set_up.set_firebase_test_data(
            project_type, "results", fixture_name, self.project_id
        )

    def tearDown(self):
        tear_down.delete_test_data(self.project_id)

    def verify_mapping_results_in_postgres(self):
        """Check that mapping_sessions and mapping_sessions_results
        contain the expected data.
        """
        pg_db = auth.postgresDB()
        expected_items_count = 252

        sql_query = (
            f"SELECT * "
            f"FROM mapping_sessions "
            f"WHERE project_id = '{self.project_id}' "
            f"AND user_id = '{self.project_id}'"
        )
        result = pg_db.retr_query(sql_query)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0][6], expected_items_count)

        q2 = (
            "SELECT msr.* "
            "FROM mapping_sessions_results msr "
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
        """Test if results are transfered for users which are not yet in Postgres."""
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
            f"SELECT * "
            f"FROM mapping_sessions "
            f"WHERE project_id = '{self.project_id}' "
            f"AND user_id = '{self.project_id}'"
        )
        result = pg_db.retr_query(sql_query)
        self.assertEqual(len(result), 1)

    def test_additional_results_for_different_group_are_not_deleted(self):
        """Test if new results are not deleted when workflow has already started.

        Here we check what happens to results that are submitted,
        when the transfer of results workflow is already running.
        We expect that these new results should remain in Firebase
        until the next run of transfer results.
        """

        fb_db = auth.firebaseDB()

        results_ref = fb_db.reference(f"v2/results/{self.project_id}")
        results = results_ref.get()

        # Add additional results in Firebase for group with key 'g115'.
        # This is the same group for which results already exist.
        # So here we simulate another user mapping a group
        # that has been mapped before already.
        # These results should not get deleted by the function below.
        test_dir = os.path.dirname(__file__)
        fixture_name = "build_area_additional_results_different_group.json"
        file_path = os.path.join(
            test_dir, "fixtures", "tile_map_service_grid", "results", fixture_name
        )

        with open(file_path) as test_file:
            new_results = json.load(test_file)

        results_ref = fb_db.reference(f"v2/results/{self.project_id}/g120")
        results_ref.set(new_results)

        # run transfer results function
        transfer_results_for_project(self.project_id, results)

        self.verify_mapping_results_in_postgres()

        # check if new results for the group 'g120' are still in Firebase
        ref = fb_db.reference(
            f"v2/results/{self.project_id}/g120/test_build_area/results"
        )
        self.assertEqual(len(ref.get(shallow=True)), 252)

    def test_additional_results_for_same_group_are_not_deleted(self):
        """Test if new results are not deleted when workflow has already started.

        Here we check what happens to results that are submitted,
        when the transfer of results workflow is already running.
        We expect that these new results should remain in Firebase
        until the next run of transfer results.
        """

        fb_db = auth.firebaseDB()

        results_ref = fb_db.reference(f"v2/results/{self.project_id}")
        results = results_ref.get()

        # Add additional results in Firebase for group with key 'g115'.
        # This is the same group for which results already exist.
        # So here we simulate another user mapping a group
        # that has been mapped before already.
        # These results should not get deleted by the function below.
        test_dir = os.path.dirname(__file__)
        fixture_name = "build_area_additional_results_same_group.json"
        file_path = os.path.join(
            test_dir, "fixtures", "tile_map_service_grid", "results", fixture_name
        )

        with open(file_path) as test_file:
            new_results = json.load(test_file)

        results_ref = fb_db.reference(f"v2/results/{self.project_id}/g115/new_user/")
        results_ref.set(new_results)

        # run transfer results function
        transfer_results_for_project(self.project_id, results)

        self.verify_mapping_results_in_postgres()

        # check if new results for the group 'g115' are still in Firebase
        ref = fb_db.reference(f"v2/results/{self.project_id}/g115/new_user/results")
        self.assertEqual(len(ref.get(shallow=True)), 252)

    def test_results_with_user_groups(self):
        pg_db = auth.postgresDB()

        # run transfer results function
        transfer_results()

        UG_QUERY = "SELECT user_group_id FROM user_groups ORDER BY user_group_id"
        RUG_QUERY = """
            SELECT user_group_id
            FROM mapping_sessions_user_groups
            ORDER BY user_group_id
        """
        for query, expected_value in [
            (
                UG_QUERY,
                [
                    ("dummy-user-group-1",),
                    ("dummy-user-group-2",),
                    ("dummy-user-group-4",),  # NOTE: This is a non existing group.
                ],
            ),
            (
                RUG_QUERY,
                [
                    ("dummy-user-group-1",),
                    ("dummy-user-group-2",),
                    ("dummy-user-group-4",),  # NOTE: This is a non existing group.
                ],
            ),
        ]:
            self.assertEqual(
                expected_value,
                pg_db.retr_query(UG_QUERY),
                query,
            )


if __name__ == "__main__":
    unittest.main()
