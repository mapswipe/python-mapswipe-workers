-- noinspection SqlNoDataSourceInspectionForFile
CREATE EXTENSION postgis;

CREATE TABLE IF NOT EXISTS projects (
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

CREATE TABLE IF NOT EXISTS groups (
    project_id varchar,
    group_id varchar,
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
    project_id varchar,
    group_id varchar,
    task_id varchar,
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
    user_id varchar,
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


---- User Group Tables
CREATE TABLE IF NOT EXISTS user_groups (
    user_group_id varchar,
    name varchar,
    description text,
    PRIMARY KEY (user_group_id)
);

CREATE TABLE IF NOT EXISTS user_groups_temp (
    user_group_id varchar,
    name varchar,
    description text
);

CREATE TABLE IF NOT EXISTS user_groups_user_memberships (
    user_group_id varchar,
    user_id varchar,
    is_active boolean,
    PRIMARY KEY (user_group_id, user_id),
    FOREIGN KEY (user_id) REFERENCES users (user_id),
    FOREIGN KEY (user_group_id) REFERENCES user_groups (user_group_id)
);

CREATE TABLE IF NOT EXISTS user_groups_user_memberships_temp (
    user_group_id varchar,
    user_id varchar
);

-- Used to group results by user groups
CREATE TABLE IF NOT EXISTS results_user_groups (
    -- result primary key (not using task_id as it is a flat field in results)
    project_id varchar,
    group_id varchar,
    user_id varchar,
    -- user group primary key
    user_group_id varchar,
    PRIMARY KEY (project_id, group_id, user_id, user_group_id),
    FOREIGN KEY (project_id) REFERENCES projects (project_id),
    FOREIGN KEY (user_id) REFERENCES users (user_id),
    FOREIGN KEY (user_group_id) REFERENCES user_groups (user_group_id),
    FOREIGN KEY (project_id, group_id) REFERENCES groups (project_id, group_id)
);

-- create table for user_group_results import through csv
CREATE TABLE IF NOT EXISTS results_user_groups_temp (
    project_id varchar,
    group_id varchar,
    user_id varchar,
    user_group_id varchar
);
