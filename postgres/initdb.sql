-- noinspection SqlNoDataSourceInspectionForFile


CREATE EXTENSION postgis;
--
-- TABLES
--
CREATE TABLE IF NOT EXISTS projects (
    archive boolean,
    created timestamp,
    created_by varchar,
    geom geometry(MULTIPOLYGON,4326),
    image varchar,
    is_featured boolean,
    look_for varchar,
    name varchar,
    progress int,
    project_details varchar,
    project_id varchar,
    project_type int,
    project_type_specifics json,
    required_results int,
    result_count int,
    status varchar,
    verification_number int,
    PRIMARY KEY(project_id)
    );

CREATE TABLE IF NOT EXISTS groups (
    project_id varchar,
    group_id varchar,
    number_of_tasks int,
    finished_count int,
    required_count int,
    progress int,
    project_type_specifics json,
    PRIMARY KEY(project_id, group_id),
    FOREIGN KEY (project_id) REFERENCES projects (project_id)
    );

CREATE INDEX IF NOT EXISTS groups_projectid ON public.groups USING btree (group_id);
CREATE INDEX IF NOT EXISTS groups_goupid ON public.groups USING btree (project_id);

CREATE TABLE IF NOT EXISTS tasks (
    project_id varchar,
    group_id varchar,
    task_id varchar,
    geom geometry(MULTIPOLYGON,4326),
    project_type_specifics json,
    PRIMARY KEY(project_id, group_id, task_id),
    FOREIGN KEY (project_id) REFERENCES projects (project_id),
    FOREIGN KEY (project_id, group_id) REFERENCES groups (project_id, group_id)
    );

CREATE INDEX IF NOT EXISTS tasks_task_id ON public.tasks USING btree (task_id);
CREATE INDEX IF NOT EXISTS tasks_groupid ON public.tasks USING btree (group_id);
CREATE INDEX IF NOT EXISTS tasks_projectid ON public.tasks USING btree (project_id);

CREATE TABLE IF NOT EXISTS users (
    user_id varchar,
    username varchar,
    created timestamp,
    PRIMARY KEY(user_id)
    );

CREATE TABLE IF NOT EXISTS results (
    project_id varchar,
    group_id varchar,
    user_id varchar,
    task_id varchar,
    "timestamp" timestamp,
    start_time timestamp DEFAULT NULL,
    end_time timestamp DEFAULT NULL,
    result int,
    PRIMARY KEY (project_id, group_id, task_id, user_id),
    FOREIGN KEY (project_id) REFERENCES projects (project_id),
    FOREIGN KEY (project_id, group_id) REFERENCES groups (project_id, group_id),
    FOREIGN KEY (project_id, group_id, task_id) REFERENCES tasks (project_id, group_id, task_id),
    FOREIGN KEY (user_id) REFERENCES users (user_id)
    );

CREATE INDEX IF NOT EXISTS results_projectid ON public.results USING btree (project_id);
CREATE INDEX IF NOT EXISTS results_groupid ON public.results USING btree (group_id);
CREATE INDEX IF NOT EXISTS results_taskid ON public.results USING btree (task_id);
CREATE INDEX IF NOT EXISTS results_userid ON public.results USING btree (user_id);

-- create table for results import through csv
CREATE TABLE IF NOT EXISTS results_temp (
    project_id varchar,
    group_id varchar,
    user_id varchar,
    task_id varchar,
    "timestamp" timestamp,
    start_time timestamp,
    end_time timestamp,
    result int,
    PRIMARY KEY (project_id, group_id, task_id, user_id),
    FOREIGN KEY (project_id) REFERENCES projects (project_id),
    FOREIGN KEY (project_id, group_id) REFERENCES groups (project_id, group_id),
    FOREIGN KEY (project_id, group_id, task_id) REFERENCES tasks (project_id, group_id, task_id),
    FOREIGN KEY (user_id) REFERENCES users (user_id)
    );

--
-- USERS
--
-- create a read-only user for backups
CREATE USER backup WITH PASSWORD 'backupuserpassword';
GRANT CONNECT ON DATABASE mapswipe TO backup;
GRANT USAGE ON SCHEMA public TO backup;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO backup;

--
-- VIEWS
--
-- create views for statistics
\i /docker-entrypoint-initdb.d/stat_views.sql
