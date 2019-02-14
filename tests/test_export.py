from mapswipe_workers.basic import BaseFunctions


def test_transfer_results():
    BaseFunctions.run_export('production', [])


if __name__ == '__main__':
    test_transfer_results()
