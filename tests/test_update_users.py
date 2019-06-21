import os

import pickle
import time
import json

from mapswipe_workers import auth
from mapswipe_workers.firebase_to_postgres import update_data


def test_update_user_data(user_ids, pg_db):
    update_data.update_user_data()
    for user_id in user_ids:
        query = '''
            SELECT user_id
            FROM user
            WHERE user_id = %s
            '''
        result = pg_db.retr_query(query, user_id)
        assert result == user_id, f'user_id: {user_id}'


def create_user(fb_db):
    ref = fb_db.reference('users/')
    user = {
        'contributions': {},
        'created': int(time.time()),
        'groupContributionCount': 0,
        'projectContributionCount': 0,
        'taskContributionCount': 0,
        'timeSpentMapping': 0,
        'username': 'test_user_2'
    }
    user_id = ref.push(user).key
    print(f'Uploaded a sample user with the id: {user_id}\n')
    save_user_id(user_id)


def save_user_id(user_id):
    filename = 'user_ids.pickle'
    if os.path.isfile(filename):
        with open(filename, 'rb') as f:
            existing_user_ids = pickle.load(f)
        user_id = existing_user_ids + user_id

    with open(filename, 'wb') as f:
        pickle.dump(user_id, f)


if __name__ == '__main__':
    pg_db = auth.postgresDB()
    fb_db = auth.firebaseDB()

    filename = 'user_ids.pickle'
    with open(filename, 'rb') as f:
        user_ids = pickle.load(f)

    test_update_user_data(user_ids, pg_db)
    create_user(fb_db)

    with open(filename, 'rb') as f:
        user_ids = pickle.load(f)

    test_update_user_data(user_ids, pg_db)

    del(fb_db)
    del(pg_db)
