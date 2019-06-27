from mapswipe_workers.firebase_to_postgres import transfer_results
from mapswipe_workers.firebase_to_postgres import update_data


update_data.copy_new_users()
transfer_results.transfer_results()
print(
        'Transfered results from Firebase to Postgres' +
        'and deleted them in Firebase'
        )
