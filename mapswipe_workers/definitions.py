import os

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.abspath(os.path.join(ROOT_DIR, 'configuration.json'))
DATA_PATH = os.path.abspath(os.path.join(ROOT_DIR, '..', 'data'))


class CustomError(Exception):
    pass
