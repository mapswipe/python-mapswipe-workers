from mapswipe_workers import transfer_results

transfer_results.run_transfer_results()

print(
        'Transfered results from Firebase to Postgres' +
        'and deleted them in Firebase'
        )
