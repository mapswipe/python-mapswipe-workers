from mapswipe_workers import mapswipe_workers


mapswipe_workers._run_create_projects()
print(
        'Created projects from existing project drafts in ' +
        'Firebase and saved them in Firebase and Postgres'
        )
