/*
 * This script takes the data from the 'results' table.
 * Results submitted before 2019-09-30 11:30:02.823
 * do NOT provide the "start_time" and "end_time" attribute,
 * but only use a single attribute "timestamp".
 * During the initial transfer this has not been considered.
 */
set search_path = 'public';

insert into mapping_sessions
(
    select
        project_id
         ,group_id
         ,user_id
         ,nextval('mapping_sessions_mapping_session_id_seq') as mapping_session_id
         ,Min(timestamp) as start_time
         ,Max(timestamp) as end_time
         ,count(*) as items_count
    from results
    where start_time is null and end_time is null
    group by project_id, group_id, user_id
)
on conflict (project_id, group_id, user_id)
DO UPDATE SET
    start_time = EXCLUDED.start_time,
    end_time = EXCLUDED.end_time;

