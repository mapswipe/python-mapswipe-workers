import pickle
import os.path
from mapswipe_workers.basic import BaseFunctions


def delete_sample_data_from_firebase(fb_db):
    fb_db.child('imports').set({})

    # if os.path.isfile('firebase_imports_keys.pickle'):
    #     with open('firebase_imports_keys.pickle', 'rb') as f:
    #         keys = pickle.load(f)
    #     os.remove('firebase_imports_keys.pickle')
    # else:
    #     raise FileNotFoundError

    # for key in keys:
    #     print(key)
    #     fb_db.child('imports').child(key).remove()


def delete_sample_groups_from_firebase(fb_db):
    fb_db.child('groups').set({})
    # os.remove('firebase_imports_keys.pickle')


def delete_sample_projects_from_firebase(fb_db):
    fb_db.child('projects').set({})


def delete_sample_results_from_postgres(p_con):
    sql_query = '''
        DELETE FROM projects;
        DELETE FROM results;
        DELETE FROM tasks;
        DELETE FROM groups;
        DELETE FROM imports;
        '''
    p_con.query(sql_query, [])


def yes_or_no(question):
    reply = str(input(question+' (y/n): ')).lower().strip()
    if reply[0] == 'y':
        return True
    if reply[0] == 'n':
        return False
    else:
        return yes_or_no("Uhhhh... please enter ")


if __name__ == '__main__':

    if yes_or_no('''\
            This will delete all data in firebase and postgres \
            (Not only the sample data). Do you wish to continue?
            '''):
        firebase, postgres = BaseFunctions.get_environment('production')
        fb_db = firebase.database()
        p_con = postgres()

        delete_sample_data_from_firebase(fb_db)
        delete_sample_groups_from_firebase(fb_db)
        delete_sample_projects_from_firebase(fb_db)
        delete_sample_results_from_postgres(p_con)

    # TODO: remove groups and projects
