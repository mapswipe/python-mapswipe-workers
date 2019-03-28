from mapswipe_workers.basic import BaseFunctions

def test_update_old_projects():

    project_ids = [3, 124, 5519, 13523]
    BaseFunctions.run_update('production', project_ids)


if __name__ == '__main__':
    test_update_old_projects()
