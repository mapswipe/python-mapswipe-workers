from mapswipe_workers.firebase_to_postgres import transfer_results
from mapswipe_workers.firebase_to_postgres import update_data

if __name__ == '__main__':
    # TODO: review copy users, we often get: "results_temp" violates foreign key constraint "results_temp_user_id_fkey"
    update_data.copy_new_users()
    # TODO: Do we need a mechanism to copy data only for specific projects?
    transfer_results.transfer_results()
