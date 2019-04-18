from mapswipe_workers import run

run._run_transfer_results()

print(
        'Transfered results from Firebase to Postgres' +
        'and deleted them in Firebase'
        )
