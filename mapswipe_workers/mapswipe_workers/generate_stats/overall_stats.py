


def get_overall_stats(filename):
    '''
    Export the aggregated results statistics as csv file.

    Parameters
    ----------
    filename: str
    -------

    '''
    pg_db = auth.postgresDB()
    sql_query = "COPY (SELECT * FROM aggregated_results) TO STDOUT WITH CSV HEADER"

    with open(filename, 'w') as f:
        pg_db.copy_expert(sql_query, f)

    del pg_db

    logger.info('saved aggregated results to %s' % filename)