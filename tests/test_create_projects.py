from mapswipe_workers import run


run._run_create_projects()
print(
        'Created projects from existing project drafts in ' +
        'Firebase and saved them in Firebase and Postgres'
        )
