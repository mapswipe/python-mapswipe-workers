from mapswipe_workers.basic import BaseFunctions
import test_init


def import_process():
    test_init.upload_sample_data_to_firebase()
    BaseFunctions.run_import('production')


if __name__ == '__main__':
    import_process()
    print("Everything passed")

# upload each import to firebase imports table



# now try to run import process with correct parameters




# check if everything has been created correctly in firebase and postgres


