from mapswipe_workers.base import base_functions


base_functions.run_create_project()
print(
        'Created projects from existing project drafts in ' +
        'Firebase and saved them in Firebase and Postgres'
        )
