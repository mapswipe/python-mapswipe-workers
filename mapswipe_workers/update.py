import csv
import io

from mapswipe_workers import auth

# TODO: Retrieve only data from firebase which recently changed
# and therefor needs to be updated in postgres.
# How can this be achived?


def update_user_data():
    fb_db = auth.firebaseDB()
    users_ref = fb_db.reference('users/')
    users = users_ref.get()

    users_file = io.StringIO('')

    w = csv.writer(
            users_file,
            delimiter='\t',
            quotechar="'"
            )

    for userId, user in users.items():
        w.writerow([
                userId,
                user['username'],
                user['contributionCount'],
                user['distance'],
                ])

    users_file.seek(0)

    fieldnames = (
            'user_id',
            'username',
            'contribution_count',
            'distance',
            )
    p_con = auth.postgresDB()
    p_con.copy_from(users_file, 'users', fieldnames)

    del(p_con)
    users_file.close()


def update_group_data():
    pass


def update_project_data():
    pass
