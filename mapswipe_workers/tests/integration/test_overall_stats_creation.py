
import os
import sys
import types

# Fake sentry_sdk
fake_sentry = types.ModuleType("sentry_sdk")
fake_sentry.init = lambda *args, **kwargs: None
fake_sentry.capture_exception = lambda *args, **kwargs: None
sys.modules["sentry_sdk"] = fake_sentry

fake_xdg = types.ModuleType("xdg")
fake_xdg.XDG_DATA_HOME = "/tmp"
sys.modules["xdg"] = fake_xdg

# Fake osgeo
fake_osgeo = types.ModuleType("osgeo")
fake_osgeo.ogr = types.ModuleType("ogr")
fake_osgeo.osr = types.ModuleType("osr")
sys.modules["osgeo"] = fake_osgeo

# Fake env vars
os.environ["FIREBASE_API_KEY"] = "dummy"
os.environ["FIREBASE_AUTH_DOMAIN"] = "dummy"
os.environ["FIREBASE_DATABASE_URL"] = "dummy"
os.environ["FIREBASE_STORAGE_BUCKET"] = "dummy"
os.environ["FIREBASE_PROJECT_ID"] = "dummy"
os.environ["FIREBASE_MESSAGING_SENDER_ID"] = "dummy"
os.environ["FIREBASE_APP_ID"] = "dummy"
os.environ["POSTGRES_PASSWORD"] = "dummy"
os.environ["OSMCHA_API_KEY"] = "dummy"
os.environ["MAPILLARY_API_KEY"] = "dummy"


import pandas as pd
from tempfile import TemporaryDirectory

from mapswipe_workers.generate_stats.overall_stats import get_overall_stats



def test_overall_stats_csv_creation():
    """
    Just making sure that get_overall_stats() actually creates a CSV
    and the numbers inside it make sense. Basically, testing that the
    aggregation logic works the way it's supposed to.
    """

    # Fake project data to simulate what the real function would see.
    df = pd.DataFrame(
        [
            {
                "project_id": "p1",
                "status": "active",
                "area_sqkm": 10,
                "number_of_results": 100,
                "number_of_results_progress": 60,
                "number_of_users": 5,
            },
            {
                "project_id": "p2",
                "status": "active",
                "area_sqkm": 20,
                "number_of_results": 200,
                "number_of_results_progress": 140,
                "number_of_users": 15,
            },
            {
                "project_id": "p3",
                "status": "finished",
                "area_sqkm": 50,
                "number_of_results": 300,
                "number_of_results_progress": 250,
                "number_of_users": 30,
            },
        ]
    )

    # Expected aggregated numbers for active projects.
    expected_active_projects = 2
    expected_active_area = 10 + 20
    expected_active_results = 100 + 200
    expected_active_results_progress = 60 + 140
    expected_active_avg_users = (5 + 15) / 2

    # Use a temp folder so we don't clutter anything in the repo.
    with TemporaryDirectory() as tmpdir:
        output_file = os.path.join(tmpdir, "overall_stats.csv")

        # Run the actual function we are testing.
        result_df = get_overall_stats(df, output_file)

        # Check that the CSV file was actually created.
        assert os.path.exists(output_file)

        # Load the CSV that the function wrote out.
        csv_df = pd.read_csv(output_file)

        # These are the columns we expect to see.
        expected_columns = [
            "status",
            "count_projects",
            "area_sqkm",
            "number_of_results",
            "number_of_results_progress",
            "average_number_of_users_per_project",
        ]

        # We sort here because pandas sometimes shuffles columns around,
        assert sorted(csv_df.columns) == sorted(expected_columns)

        # We expect exactly one row for "active" and one for "finished".
        assert len(csv_df) == 2

        # Grab the row for the active projects.
        active_row = csv_df[csv_df["status"] == "active"].iloc[0]

        # Now check actual math.
        assert active_row["count_projects"] == expected_active_projects
        assert active_row["area_sqkm"] == expected_active_area
        assert active_row["number_of_results"] == expected_active_results
        assert (
            active_row["number_of_results_progress"]
            == expected_active_results_progress
        )
        assert (
            active_row["average_number_of_users_per_project"]
            == expected_active_avg_users
        )

