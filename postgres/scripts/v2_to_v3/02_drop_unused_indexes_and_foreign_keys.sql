/*
 * This script drops unused indexes and not needef foreign keys.
 * This reduces the database size a lot.
 */
set search_path = 'replica_mini';

------------------------------------------
-- drop unused indexes
-------------------------------------------

drop index if exists groups_goupid;
drop index if exists groups_projectid;

drop index if exists results_userid;
drop index if exists results_groupid;
drop index if exists results_timestamp_date_idx;
drop index if exists results_taskid;
drop index if exists results_projectid;

-- tasks_groupid was never set as an index
drop index if exists tasks_projectid;

drop index if exists users_userid;

------------------------------------------
-- drop not needed foreign keys
-------------------------------------------
alter table tasks 
drop constraint if exists tasks_project_id_fkey;

alter table results 
drop constraint if exists results_project_id_fkey;

alter table results 
drop constraint if exists results_project_id_fkey1;
