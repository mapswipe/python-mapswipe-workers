import csv
import io

from mapswipe_workers import auth


def run_transfer_results():
    """
    Download results from firebase,
    saves them to postgres and then deletes the results in firebase.

    Returns
    -------
    bool
        True if successful, False otherwise
    """

    fb_db = auth.firebaseDB()
    results_ref = fb_db.reference('results')

    results = results_ref.get()
    results_file = results_to_file(results)
    save_results_to_postgres(results_file)

    del(fb_db)

    # TODO: Delete block comment if transfer_results is finalized

    # users_ref = fb_db.reference('users')
    # users = users_ref.get()
    # save_users_to_postgres(users)

    # p_con = auth.postgresDB()
    # sql_insert = '''
    #         DELETE FROM results;
    #         '''
    # p_con.query(sql_insert, None)
    # del p_con

    # start = time.time()
    # results_txt_filename = results_to_txt(results)
    # save_batch_results_postgres(results_txt_filename)
    # end = time.time()
    # print(end-start)


# def save_results_postgres(results):
#     p_con = auth.postgresDB()

#     sql_insert = '''
#             INSERT INTO results
#             VALUES (%s, %s, %s, %s, %s, %s)
#             '''
#     counter = 0
#     for projectId, groups in results.items():
#         for groupId, users in groups.items():
#             for userId, results in users.items():
#                 try:
#                     resultCount = results['resultCount']
#                     del(results['resultCount'])
#                 except:
#                     pass
#                 try:
#                     timestamp = results['timestamp']
#                     del(results['timestamp'])
#                 except:
#                     pass
#                 for taskId, result in results.items():
#                     counter = counter + 1
#                     data_result = [
#                             projectId,
#                             groupId,
#                             userId,
#                             taskId,
#                             0,
#                             result
#                             ]
#                     print(data_result)
#                     p_con.query(sql_insert, data_result)
#     del p_con
#     print(counter)
#     return True


def save_results_to_postgres(results_file):
    try:
        p_con = auth.postgresDB()
        # with open(results_filename, 'r') as f:
        columns = [
                'project_id',
                'group_id',
                'user_id',
                'task_id',
                'timestamp',
                'result'
                ]
        p_con.copy_from(results_file, 'results', sep='\t', columns=columns)
        del p_con
        return True
    except Exception:
        return False


def results_to_file(results):
    '''

    Writes results to an in-memory file like object
    formatted as a csv using the buffer module (StringIO).
    This can be then used by the COPY statement of Postgres
    for a more efficient import of many results into the Postgres
    instance.

    Parameters
    ----------
    results: dict
        The results as retrived from the Firebase Realtime Database instance.

    Returns
    -------
    results_file: object
        The results in an StringIO buffer.
    '''
    # TODO: infer from resultCount and
    # existing results how many no where generated

    # If csv file is a file object, it should be opened with newline=''
    results_file = io.StringIO('')

    fieldnames = (
            'project_id',
            'group_id',
            'user_id',
            'task_id',
            'timestamp',
            'result'
            )
    w = csv.DictWriter(
            results_file,
            fieldnames=fieldnames,
            delimiter='\t',
            quotechar="'"
            )
    for projectId, groups in results.items():
        for groupId, users in groups.items():
            for userId, results in users.items():
                # TODO: Improve try except statement
                # There should be no need for try except
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
                    output_dict = {
                            "project_id": projectId,
                            "group_id": groupId,
                            "user_id": userId,
                            "task_id": taskId,
                            "timestamp": 0,
                            "result": result
                            }
                    w.writerow(output_dict)
    results_file.close()
    return results_file


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
