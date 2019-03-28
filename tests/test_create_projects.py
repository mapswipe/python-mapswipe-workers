from mapswipe_workers.base import base_functions
import logging
import sys

def test_import_process():
    base_functions.run_create_project()


if __name__ == '__main__':
    test_import_process()
    print("Everything passed")
