create schema if not exists without_int_id;

set search_path = without_int_id, public;

CREATE TABLE IF NOT EXISTS projects (
    project_id varchar,
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

CREATE TABLE IF NOT EXISTS users (
    user_id varchar,
    username varchar,
    created timestamp,
    PRIMARY KEY (user_id)
);

CREATE TABLE IF NOT EXISTS users_temp (
    user_id varchar,
    username varchar,
    created timestamp
);

CREATE TABLE IF NOT EXISTS group_results (
    result_id SERIAL unique,
    project_id varchar,
    group_id varchar,
    user_id varchar,
    "timestamp" timestamp,
    session_length INTERVAL DEFAULT NULL,
    result_count int,
    PRIMARY KEY (project_id, group_id, user_id),
    FOREIGN KEY (project_id) REFERENCES projects (project_id),
    FOREIGN KEY (project_id, group_id) REFERENCES groups (project_id, group_id),
    FOREIGN KEY (user_id) REFERENCES users (user_id)
);

CREATE INDEX IF NOT EXISTS without_int_group_results_result_id ON without_int_id.group_results
    USING btree (result_id);

CREATE INDEX IF NOT EXISTS  without_int_group_results_timestamp_date_idx
    ON without_int_id.group_results ("timestamp" DESC);

CREATE TABLE IF NOT EXISTS results (
    task_id varchar,
    result_id int,
    result int,
    PRIMARY KEY (result_id, task_id),
    FOREIGN KEY (result_id) REFERENCES group_results (result_id)
);

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