import os
import json

TEST_DIR = os.path.dirname(os.path.abspath(__file__))
FIXTURE_DIR = os.path.join(TEST_DIR, "fixtures")


def get_fixture(path):
    file_path = os.path.join(FIXTURE_DIR, path)
    with open(file_path) as file:
        return json.load(file)
