from mapswipe_workers.basic import BaseFunctions


def test_import_process():
    BaseFunctions.run_create_project()


if __name__ == '__main__':
    test_import_process()
    print("Everything passed")
