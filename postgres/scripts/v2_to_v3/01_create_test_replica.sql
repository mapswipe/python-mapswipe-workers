/*
 * This creates a subset of the existing MapSwipe database
 * and copies all data for the 10 most recently created projects
 * to a new schema called 'replica_mini'.
 */

drop schema "replica_mini" cascade;
create schema "replica_mini";

drop table if exists "replica_mini".projects cascade;
drop table if exists "replica_mini".results cascade;
drop table if exists "replica_mini".groups cascade;
drop table if exists "replica_mini".tasks cascade;
drop table if exists "replica_mini".users cascade;


------------------------------------------
-- create tables for mini replica
-------------------------------------------

CREATE TABLE IF NOT EXISTS "replica_mini".projects (
    created timestamp,
    created_by varchar,
    geom geometry,
    image varchar,
    is_featured boolean,
    look_for varchar,
    name varchar,
    progress int,
    project_details varchar,
    project_id varchar,
    project_type int,
    required_results int,
    result_count int,
    status varchar,
    verification_number int,
    project_type_specifics json,
    PRIMARY KEY (project_id)
);

CREATE TABLE IF NOT EXISTS "replica_mini".groups (
    project_id varchar,
    group_id varchar,
    number_of_tasks int,
    finished_count int,
    required_count int,
    progress int,
    project_type_specifics json,
    PRIMARY KEY (project_id, group_id),
    FOREIGN KEY (project_id) REFERENCES "replica_mini".projects (project_id)
);

CREATE INDEX IF NOT EXISTS groups_projectid ON "replica_mini".groups
    USING btree (group_id);

CREATE INDEX IF NOT EXISTS groups_goupid ON "replica_mini".groups
    USING btree (project_id);

CREATE TABLE IF NOT EXISTS "replica_mini".tasks (
    project_id varchar,
    group_id varchar,
    task_id varchar,
    geom geometry(MULTIPOLYGON, 4326),
    project_type_specifics json,
    PRIMARY KEY (project_id, group_id, task_id),
    FOREIGN KEY (project_id) REFERENCES "replica_mini".projects (project_id),
    FOREIGN KEY (project_id, group_id) REFERENCES "replica_mini".groups (project_id, group_id)
);

CREATE INDEX IF NOT EXISTS tasks_task_id ON "replica_mini".tasks
    USING btree (task_id);

CREATE INDEX IF NOT EXISTS tasks_groupid ON "replica_mini".tasks
    USING btree (group_id);

CREATE INDEX IF NOT EXISTS tasks_projectid ON "replica_mini".tasks
    USING btree (project_id);

CREATE TABLE IF NOT EXISTS "replica_mini".users (
    user_id varchar,
    username varchar,
    created timestamp,
    PRIMARY KEY (user_id)
);

CREATE INDEX IF NOT EXISTS users_userid ON "replica_mini".users
    USING btree (user_id);

   -- Do we need this table?!
CREATE TABLE IF NOT EXISTS "replica_mini".users_temp (
    user_id varchar,
    username varchar,
    created timestamp
);

CREATE TABLE IF NOT EXISTS "replica_mini".results (
    project_id varchar,
    group_id varchar,
    user_id varchar,
    task_id varchar,
    "timestamp" timestamp,
    start_time timestamp DEFAULT NULL,
    end_time timestamp DEFAULT NULL,
    result int,
    PRIMARY KEY (project_id, group_id, task_id, user_id),
    FOREIGN KEY (project_id) REFERENCES "replica_mini".projects (project_id),
    FOREIGN KEY (project_id, group_id) REFERENCES "replica_mini".groups (project_id, group_id),
    FOREIGN KEY (project_id, group_id, task_id) REFERENCES "replica_mini".tasks (project_id, group_id, task_id),
    FOREIGN KEY (user_id) REFERENCES "replica_mini".users (user_id)
);

CREATE INDEX IF NOT EXISTS results_projectid ON "replica_mini".results
    USING btree (project_id);

CREATE INDEX IF NOT EXISTS results_groupid ON "replica_mini".results
    USING btree (group_id);

CREATE INDEX IF NOT EXISTS results_taskid ON "replica_mini".results
    USING btree (task_id);

CREATE INDEX IF NOT EXISTS results_userid ON "replica_mini".results
    USING btree (user_id);

CREATE INDEX IF NOT EXISTS results_timestamp_date_idx
    ON "replica_mini".results ("timestamp" DESC);


-- create table for results import through csv
CREATE TABLE IF NOT EXISTS "replica_mini".results_temp (
    project_id varchar,
    group_id varchar,
    user_id varchar,
    task_id varchar,
    "timestamp" timestamp,
    start_time timestamp,
    end_time timestamp,
    result int
);

------------------------------------------
-- Insert subset of the data
-------------------------------------------

insert into "replica_mini".projects (
	select
		*
	from projects p 
	where created > '2022-05-01'
	limit 10
);

insert into "replica_mini".groups
(
select g.*
from groups g, "replica_mini".projects p
where g.project_id = p.project_id
);


insert into "replica_mini".tasks
(
select t.*
from tasks t, "replica_mini".projects p
where t.project_id = p.project_id
);

insert into "replica_mini".users
(
select *
from users u 
);

insert into "replica_mini".results
(
select r.*
from results r, "replica_mini".projects p
where r.project_id = p.project_id
);

------------------------------------------
-- check tables
-------------------------------------------

SELECT
  schema_name,
  relname,
  pg_size_pretty(table_size) AS size,
  table_size
FROM (
       SELECT
         pg_catalog.pg_namespace.nspname           AS schema_name,
         relname,
         pg_relation_size(pg_catalog.pg_class.oid) AS table_size
       FROM pg_catalog.pg_class
         JOIN pg_catalog.pg_namespace ON relnamespace = pg_catalog.pg_namespace.oid
     ) t
WHERE schema_name = 'replica_mini' AND table_size > 0 ORDER BY table_size DESC;


