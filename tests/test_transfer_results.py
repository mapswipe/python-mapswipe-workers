from mapswipe_workers import mapswipe_workers

mapswipe_workers._run_transfer_results()

print(
        'Transfered results from Firebase to Postgres' +
        'and deleted them in Firebase'
        )
