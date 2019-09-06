from mapswipe_workers.firebase_to_postgres import transfer_results
from mapswipe_workers.firebase_to_postgres import update_data

if __name__ == '__main__':
    # TODO: Do we need a mechanism to copy data only for specific users or projects?
    # TODO: check copy_new_users, are newly created users copied correctly
    update_data.copy_new_users()
    transfer_results.transfer_results()
