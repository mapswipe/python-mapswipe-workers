-- noinspection SqlNoDataSourceInspectionForFile
CREATE EXTENSION postgis;

CREATE TABLE IF NOT EXISTS projects (
    project_id SERIAL,
    firebase_project_id varchar,
    created timestamp,
    created_by varchar,
    geom geometry,
    image varchar,
    is_featured boolean,
    look_for varchar,
    name varchar,
    progress int,
    project_details varchar,
    project_type int,
    required_results int,
    result_count int,
    status varchar,
    verification_number int,
    project_type_specifics json,
    PRIMARY KEY (project_id)
);

CREATE TABLE IF NOT EXISTS groups (
    project_id int,
    group_id SERIAL,
    firebase_group_id varchar,
    number_of_tasks int,
    finished_count int,
    required_count int,
    progress int,
    project_type_specifics json,
    PRIMARY KEY (project_id, group_id),
    FOREIGN KEY (project_id) REFERENCES projects (project_id)
);

CREATE INDEX IF NOT EXISTS groups_projectid ON public.groups
    USING btree (group_id);

CREATE INDEX IF NOT EXISTS groups_goupid ON public.groups
    USING btree (project_id);

CREATE TABLE IF NOT EXISTS tasks (
    project_id int,
    group_id int,
    task_id int,
    firebase_task_id varchar,
    geom geometry(MULTIPOLYGON, 4326),
    project_type_specifics json,
    PRIMARY KEY (project_id, group_id, task_id),
    FOREIGN KEY (project_id) REFERENCES projects (project_id),
    FOREIGN KEY (project_id, group_id) REFERENCES groups (project_id, group_id)
);

CREATE INDEX IF NOT EXISTS tasks_task_id ON public.tasks
    USING btree (task_id);

CREATE INDEX IF NOT EXISTS tasks_groupid ON public.tasks
    USING btree (group_id);

CREATE INDEX IF NOT EXISTS tasks_projectid ON public.tasks
    USING btree (project_id);

CREATE TABLE IF NOT EXISTS users (
    user_id SERIAL,
    firebase_user_id varchar,
    username varchar,
    created timestamp,
    PRIMARY KEY (user_id)
);

CREATE INDEX IF NOT EXISTS users_userid ON public.users
    USING btree (user_id);

CREATE TABLE IF NOT EXISTS users_temp (
    user_id varchar,
    username varchar,
    created timestamp
);

CREATE TABLE IF NOT EXISTS results (
    task_id int,
    result_id int,
    result int,
    PRIMARY KEY (result_id, task_id),
    FOREIGN KEY (result_id) REFERENCES group_results (result_id)
    FOREIGN KEY (task_id) REFERENCES tasks (task_id)
);

CREATE TABLE IF NOT EXISTS group_results (
    result_id SERIAL,
    project_id int,
    group_id int,
    user_id int,
    "timestamp" timestamp,
    session_length INTERVAL DEFAULT NULL,
    result_count int,
    PRIMARY KEY (project_id, group_id, task_id, user_id),
    FOREIGN KEY (project_id) REFERENCES projects (project_id),
    FOREIGN KEY (project_id, group_id) REFERENCES groups (project_id, group_id),
    FOREIGN KEY (project_id, group_id, task_id) REFERENCES tasks (project_id, group_id, task_id),
    FOREIGN KEY (user_id) REFERENCES users (user_id)
);

CREATE INDEX IF NOT EXISTS results_projectid ON public.results
    USING btree (project_id);

CREATE INDEX IF NOT EXISTS results_groupid ON public.results
    USING btree (group_id);

CREATE INDEX IF NOT EXISTS results_taskid ON public.results
    USING btree (task_id);

CREATE INDEX IF NOT EXISTS results_userid ON public.results
    USING btree (user_id);

CREATE INDEX IF NOT EXISTS results_timestamp_date_idx
    ON public.results ("timestamp" DESC);


-- create table for results import through csv
CREATE TABLE IF NOT EXISTS results_temp (
    project_id varchar,
    group_id varchar,
    user_id varchar,
    task_id varchar,
    "timestamp" timestamp,
    start_time timestamp,
    end_time timestamp,
    result int
);

