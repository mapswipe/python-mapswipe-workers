import sys

import pandas as pd

from mapswipe_workers import auth
from mapswipe_workers.definitions import logger


def copy_results_batch(first_timestamp, last_timestamp):
    logger.info(
        f"Start process for : ms.start_time>={first_timestamp} "
        f"and ms.start_time<{last_timestamp}"
    )
    p_con = auth.postgresDB()
    query = """
        -- create table with results for given time span
        drop table if exists results_batch;
        create table results_batch as
        select r.*
        from mapping_sessions ms, results r
        where
            ms.start_time >= %(first_timestamp)s
            and ms.start_time < %(last_timestamp)s
            and ms.project_id = r.project_id
            and ms.group_id = r.group_id
            and ms.user_id = r.user_id;
        insert into mapping_sessions_results
        (
        select
            m.mapping_session_id
            ,r.task_id
            ,r."result"
        from results_batch r, mapping_sessions m
        where
            r.project_id = m.project_id and
            r.group_id = m.group_id and
            r.user_id = m.user_id
        )
        on conflict do nothing;
    """
    p_con.query(
        query, {"first_timestamp": first_timestamp, "last_timestamp": last_timestamp}
    )
    logger.info(
        f"Finished process for : ms.start_time >= {first_timestamp} "
        f"and ms.start_time < {last_timestamp}"
    )


if __name__ == "__main__":
    """Use this command to run in docker container.
    docker-compose run -d mapswipe_workers_creation python3 python_scripts/results_to_mapping_sessions_results.py "2016-01-01" "2022-10-01"  # noqa
    """
    min_timestamp = sys.argv[1]
    max_timestamp = sys.argv[2]
    timestamps_list = (
        pd.date_range(min_timestamp, max_timestamp, freq="MS")
        .strftime("%Y-%m-%d")
        .tolist()
    )

    for i in range(0, len(timestamps_list) - 1):
        first_timestamp = timestamps_list[i]
        last_timestamp = timestamps_list[i + 1]
        copy_results_batch(first_timestamp, last_timestamp)
        logger.info(f"progress: {i+1}/{len(timestamps_list) - 1}")
