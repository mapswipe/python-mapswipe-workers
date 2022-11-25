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





-- there are about 4.2 Million records for these project ids:
--    -NBOh0mZWWn7zDn5i9Tq
--    -NBOhCDaQSPYPMeVfA10
--    -NE57yTnPUi_tR-Be8XB
--    -NEaR6DbJAbkpYJ_BDCH
--    -NEaU7GXxWRqKaFUYp_2
--    -NFNqeu6lxjAAn2RGIow
--    -NFNqqMf1_Cd5jjdAxcX
--    -NFNr1ga2uSvgkHxWAu_
--    -NFNr55R_LYJvxP7wmte
--    -NFx1-XIxP8hdA_bVIYe
--    -NH0GpIGfF2pu7V_sPnP
select count(r.*)
from mapping_sessions ms, results r
where ms.start_time >= '2022-10-01'
    and ms.project_id = r.project_id
    and ms.group_id = r.group_id
    and ms.user_id = r.user_id;

-- create table with results for projects with mapping since 2022-11-01
drop table if exists results_since_2022_10_01;
create table results_since_2022_10_01 as
select r.*
from mapping_sessions ms, results r
where ms.start_time >= '2022-10-01'
    and ms.project_id = r.project_id
    and ms.group_id = r.group_id
    and ms.user_id = r.user_id;

insert into mapping_sessions_results
(
select
    m.mapping_session_id
    ,r.task_id
    ,r."result"
from results_since_2022_10_01 r, mapping_sessions m
where
    r.project_id = m.project_id and
    r.group_id = m.group_id and
    r.user_id = m.user_id
)
on conflict do nothing;