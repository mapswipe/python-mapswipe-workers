/*
 * This script takes the data from the 'results' table
 * and transfers them to the new tables
 * - 'mapping_sessions' and
 * - 'mapping_sessions_results'
 */
set search_path = 'public';

insert into mapping_sessions
(
select
  project_id
  ,group_id
  ,user_id
  ,nextval('mapping_sessions_mapping_session_id_seq') as mapping_session_id
  ,Min(start_time) as start_time
  ,Max(end_time) as end_time
  ,count(*) as items_count
from results
group by project_id, group_id, user_id
)
on conflict do nothing;


insert into mapping_sessions_results
(
select
    m.mapping_session_id
    ,r.task_id
    ,r."result"
from results r, mapping_sessions m
where
    r.project_id = m.project_id and
    r.group_id = m.group_id and
    r.user_id = m.user_id
)
on conflict do nothing;

select count(*) from results;
select sum(items_count) from mapping_sessions;
select count(*) from mapping_sessions_results;
