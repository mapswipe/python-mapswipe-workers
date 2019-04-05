import time
import csv

from mapswipe_workers import auth


def transfer_results():
    """
    Download results from firebase,
    saves them to postgres and then deletes the results in firebase.

    Returns
    -------
    bool
        True if successful, False otherwise
    """

    fb_db = auth.firebaseDB()

    users_ref = fb_db.reference('users')
    users = users_ref.get()

    results_ref = fb_db.reference('results')
    results = results_ref.get()

    #save_users_to_postgres(users)

    start = time.time()
    save_results_postgres(results)
    end = time.time()
    print(end-start)

    p_con = auth.postgresDB()

    sql_insert = '''
            DELETE FROM results;
            '''
    p_con.query(sql_insert, None)
    del p_con

    start = time.time()
    results_txt_filename = results_to_txt(results)
    save_batch_results_postgres(results_txt_filename)
    end = time.time()
    print(end-start)


def save_results_postgres(results):
    # TODO: infer from resultCount and
    # existing results how many no where generated
    p_con = auth.postgresDB()

    sql_insert = '''
            INSERT INTO results
            VALUES (%s, %s, %s, %s, %s, %s)
            '''
    counter = 0
    for projectId, groups in results.items():
        for groupId, users in groups.items():
            for userId, results in users.items():
                try:
                    resultCount = results['resultCount']
                    del(results['resultCount'])
                except:
                    pass
                try:
                    timestamp = results['timestamp']
                    del(results['timestamp'])
                except:
                    pass
                for taskId, result in results.items():
                    counter = counter + 1
                    data_result = [
                            projectId,
                            groupId,
                            userId,
                            taskId,
                            0,
                            result
                            ]
                    print(data_result)
                    p_con.query(sql_insert, data_result)
    del p_con
    print(counter)
    return True


def save_batch_results_postgres(results_filename):
    p_con = auth.postgresDB()

    f = open(results_filename, 'r')
    with open(results_filename, 'r') as f:
        columns = [
                'project_id',
                'group_id',
                'user_id',
                'task_id',
                'timestamp',
                'result'
                ]
        p_con.copy_from(f, 'results', sep='\t', columns=columns)
    del p_con
    return True


def results_to_txt(results):

    results_txt_filename = 'raw_results.txt'

    # If csv file is a file object, it should be opened with newline=''
    results_txt_file = open(results_txt_filename, 'w', newline='')

    fieldnames = (
            'project_id',
            'group_id',
            'user_id',
            'task_id',
            'timestamp',
            'result'
            )
    w = csv.DictWriter(
            results_txt_file,
            fieldnames=fieldnames,
            delimiter='\t',
            quotechar="'"
            )
    counter = 0
    for projectId, groups in results.items():
        for groupId, users in groups.items():
            for userId, results in users.items():
                try:
                    resultCount = results['resultCount']
                    del(results['resultCount'])
                except:
                    pass
                try:
                    timestamp = results['timestamp']
                    del(results['timestamp'])
                except:
                    pass
                for taskId, result in results.items():
                    counter = counter + 1
                    output_dict = {
                            "project_id": projectId,
                            "group_id": groupId,
                            "user_id": userId,
                            "task_id": taskId,
                            "timestamp": 0,
                            "result": result
                            }
                    w.writerow(output_dict)
    results_txt_file.close()
    print(counter)
    return results_txt_filename


def save_users_to_postgres(users):
    p_con = auth.postgresDB()

    sql_insert = '''
            INSERT INTO users
            VALUES (%s, %s, %s, %s)
            '''

    for user_id, user in users.items():
        data_user = [
                user_id,
                user['contributedCount'],
                user['distance'],
                user['username'],
                ]
        p_con.query(sql_insert, data_user)

    del p_con


def delete_results_firebase():
    pass
