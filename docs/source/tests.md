# Operational Tests
The operational tests should check the usual workflows we are having with MapSwipe:
* project creation 
* mapping
* firebase to postgres transfer of results
* generate statistics based on postgres tables

To run all tests you can simply run `bash test_00_main.sh`. There are still some uncovered bits, you find them in #158. Once you created some projects, you also run the `test_02_mapping.py` script several times. Make sure to clean up after you finish testing.

## Test Project Creation
* `test_01_create_projects.py` 
* creates a user in firebase with project manager credentials
* login as project manager through firebase REST api
* set `projectDrafts` in firebase through firebase REST api, authenticated as project manager
* save project_ids to disk (to be able to delete those specific projects at a later stage of testing)
* run mapswipe workers project creation workflow through `_run_create_projects()`
* delete project manager in firebase

## Test Mapping
* `test_02_mapping.py`
* create X users (without project manager credentials)
* save users to disk (to be able to delete those specific users at a later stage of testing)
* get projects which have been created by `test_01_create_projects.py`
* get firebase projects, groups and results before mapping and save to disk
* for each user and project set random results for X groups in firebase through REST api, authenticated as normal user
* get firebase projects, groups and results after mapping and save to disk
* compare firebase before and after data

## Test Firebase to Postgres
* `test_03_firebase_to_postgres.py`
* copy new users from firebase to postgres
* copy all results from firebase to postgres

## Generate Stats
* `test_04_generate_stats.py`
* generate csv files for all projects and users for which we got results since a timestamp defined in `last_update.txt`

## Other
* we don't have broader checks of firebase database rules
* some database rules are checked indirectly, e.g. firebase read, write rules through REST api get, set requests during `test_02_mapping.py`
