import csv
import io
import datetime as dt
import dateutil.parser

from mapswipe_workers import auth
from mapswipe_workers.definitions import logger
from mapswipe_workers.firebase_to_postgres import update_data
from mapswipe_workers.utils import sentry


def transfer_results(project_id_list=None):
    '''
    Download results from firebase,
    saves them to postgres and then deletes the results in firebase.
    This is implemented as a transactional operation as described in
    the Firebase docs to avoid missing new generated results in
    Firebase during execution of this function.
    '''
    # TODO: return true if results where transfered
    # return fals if not

    # Firebase transaction function
    def transfer(current_results):
        if current_results is None:
            logger.info(f'{project_id}: No results in Firebase')
            return dict()
        else:
            results_user_id_list = get_user_ids_from_results(current_results)
            update_data.update_user_data(results_user_id_list)
            results_file = results_to_file(current_results, project_id)
            save_results_to_postgres(results_file)
            return dict()

    fb_db = auth.firebaseDB()

    if not project_id_list:
        # get project_ids from existing results if no project ids specified
        project_id_list = fb_db.reference('v2/results/').get(shallow=True)
        if not project_id_list:
            project_id_list = []
            logger.info(f'There are no results to transfer.')


    for project_id in project_id_list:
        logger.info(f'{project_id}: Start transfering results')
        if 'tutorial' in project_id:
            logger.info(f'{project_id}: these are results for a tutorial. we will not transfer these')
            continue
        results_ref = fb_db.reference(f'v2/results/{project_id}')
        truncate_temp_results()

        try:
            results_ref.transaction(transfer)
            logger.info(f'{project_id}: Transfered results to postgres')
        except fb_db.TransactionError:
            logger.exception(
                f'{project_id}: Firebase transaction for transfering results failed to commit'
            )

    del fb_db
    return


def results_to_file(results, projectId):
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
    # If csv file is a file object, it should be opened with newline=''

    results_file = io.StringIO('')

    w = csv.writer(
            results_file,
            delimiter='\t',
            quotechar="'"
            )

    logger.info(f'Got %s groups for project {projectId} to transfer' % len(results.items()))
    for groupId, users in results.items():
        for userId, results in users.items():

            # check if all attributes are set, if not don't transfer the results for this group
            try:
                timestamp = results['timestamp']
                start_time = results['startTime']
                end_time = results['endTime']
                results = results['results']
            except KeyError as e:
                sentry.capture_exception_sentry(e)
                sentry.capture_message_sentry(f'at least one missing attribute for: {projectId}/{groupId}/{userId}, will skip this one')
                logger.exception(e)
                logger.warning(f'at least one missing attribute for: {projectId}/{groupId}/{userId}, will skip this one')
                continue

            # Convert timestamp (ISO 8601) from string to a datetime object
            # this solution works only in python 3.7
            # timestamp = dt.datetime.strptime(timestamp, '%Y-%m-%dT%H:%M:%S.%f%z')
            # start_time = dt.datetime.strptime(start_time, '%Y-%m-%dT%H:%M:%S.%f%z')
            # end_time = dt.datetime.strptime(end_time, '%Y-%m-%dT%H:%M:%S.%f%z')

            timestamp = dateutil.parser.parse(timestamp)
            start_time = dateutil.parser.parse(start_time)
            end_time = dateutil.parser.parse(end_time)

            if type(results) is dict:
                for taskId, result in results.items():
                    w.writerow([
                        projectId,
                        groupId,
                        userId,
                        taskId,
                        timestamp,
                        start_time,
                        end_time,
                        result,
                        ])
            elif type(results) is list:
                # TODO: optimize for performance
                # (make sure data from firebase is always a dict)
                # if key is a integer firebase will return a list
                # if first key (list index) is 5
                # list indicies 0-4 will have value None
                for taskId, result in enumerate(results):
                    if result is None:
                        continue
                    else:
                        w.writerow([
                            projectId,
                            groupId,
                            userId,
                            taskId,
                            timestamp,
                            start_time,
                            end_time,
                            result,
                            ])
            else:
                raise TypeError

    results_file.seek(0)
    return results_file


def save_results_to_postgres(results_file):
    '''
    Saves results to a temporary table in postgres using the COPY Statement of Postgres
    for a more efficient import into the database.

    Parameters
    ----------
    results_file: io.StringIO
    '''

    p_con = auth.postgresDB()
    columns = [
            'project_id',
            'group_id',
            'user_id',
            'task_id',
            'timestamp',
            'start_time',
            'end_time',
            'result',
            ]
    p_con.copy_from(results_file, 'results_temp', columns)
    results_file.close()

    query_insert_results = '''
        INSERT INTO results
            SELECT * FROM results_temp
        ON CONFLICT (project_id,group_id,user_id,task_id)
        DO NOTHING;
    '''
    p_con.query(query_insert_results)
    del(p_con)


def truncate_temp_results():
    p_con = auth.postgresDB()
    query_truncate_temp_results = '''
                    TRUNCATE results_temp
                '''
    p_con.query(query_truncate_temp_results)
    del p_con

    return


def get_user_ids_from_results(results):
    '''
    Get all users based on the ids provided in the results
    '''

    user_ids = set([])
    for groupId, users in results.items():
        for userId, results in users.items():
            user_ids.add(userId)

    return user_ids