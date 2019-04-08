import csv
import io

from mapswipe_workers import auth
from mapswipe_workers.definitions import logger


def run_transfer_results():
    '''

    Download results from firebase,
    saves them to postgres and then deletes the results in firebase.
    This is implemented as a transactional operation as described in
    the Firebase docs to avoid missing new generated results in
    Firebase during execution of this function.

    '''

    logger.info('Start transfering results')

    fb_db = auth.firebaseDB()
    results_ref = fb_db.reference('results/')

    # Firebase transaction function
    def transfer(current_results):
        if current_results is None:
            logger.info('No results in Firebase')
            return dict()
        else:
            results_file = results_to_file(current_results)
            save_results_to_postgres(results_file)
            return dict()

    try:
        results_ref.transaction(transfer)
        logger.info('Firebase transaction for transfering results completed')
    except fb_db.TransactionError:
        logger.exception(
                'Firebase transaction for transfering results failed to commit'
                )

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
    '''

    Saves results to postgres using the COPY Statement of Postgres
    for a more efficient import into the database.

    Parameters
    ----------
    results_file: io.StringIO

    Returns
    -------
    boolean: boolean
        True if successful. False otherwise.

    '''

    try:
        p_con = auth.postgresDB()
        columns = [
                'project_id',
                'group_id',
                'user_id',
                'task_id',
                'timestamp',
                'result'
                ]
        p_con.copy_from(results_file, 'results', columns)
        del p_con
        results_file.close()
        logger.info('Successfully saved results to Postgres')
        return True
    except Exception:
        logger.exception('Could not save results to Postgres')
        raise


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
    results_file: io.StingIO
        The results in an StringIO buffer.

    '''
    # TODO: infer from resultCount and
    # existing results how many no where generated

    # If csv file is a file object, it should be opened with newline=''

    results_file = io.StringIO('')

    print(results)

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
    return results_file


def save_users_to_postgres(users):
    # TODO: Update user details in postgres
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
