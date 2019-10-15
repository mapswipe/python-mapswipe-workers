def get_aggregated_results_by_user_id(filename):
    '''
    Export aggregated results on a user_id basis as csv file.
    Parameters
    ----------
    filename: str

    Returns
    -------

    '''

    pg_db = auth.postgresDB()
    sql_query = "COPY (SELECT * FROM aggregated_results_by_user_id) TO STDOUT WITH CSV HEADER"

    with open(filename, 'w') as f:
        pg_db.copy_expert(sql_query, f)

    del pg_db

    logger.info('saved aggregated results by user_id to %s' % filename)


def get_aggregated_results_by_user_id_and_date(filename, user_id):
    '''
    Export results aggregated on user_id and daily basis as csv file.

    Parameters
    ----------
    filename: str
    user_id: str
    '''

    pg_db = auth.postgresDB()
    sql_query = sql.SQL(
        "COPY (SELECT * FROM aggregated_results_by_user_id_and_date WHERE user_id = {}) TO STDOUT WITH CSV HEADER").format(
        sql.Literal(user_id))

    with open(filename, 'w') as f:
        pg_db.copy_expert(sql_query, f)

    del pg_db

    logger.info('saved aggregated results by user_id and date for user %s to %s' % (user_id, filename))