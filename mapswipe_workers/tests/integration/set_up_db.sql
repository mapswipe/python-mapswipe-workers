CREATE EXTENSION IF NOT EXISTS postgis;

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
    organization_name varchar,
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
    updated_at timestamp,
    PRIMARY KEY (user_id)
);

CREATE INDEX IF NOT EXISTS users_userid ON public.users
    USING btree (user_id);

CREATE TABLE IF NOT EXISTS users_temp (
    user_id varchar,
    username varchar,
    created timestamp,
    updated_at timestamp
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

-- create table for results import through csv
CREATE TABLE IF NOT EXISTS results_geometry_temp (
    project_id varchar,
    group_id varchar,
    user_id varchar,
    task_id varchar,
    "timestamp" timestamp,
    start_time timestamp,
    end_time timestamp,
    result varchar
);


---- User Group Tables
CREATE TABLE IF NOT EXISTS user_groups (
    user_group_id varchar,
    name varchar,
    description text,
    is_archived boolean,
    created_at timestamp,
    archived_at timestamp,
    created_by_id varchar,
    archived_by_id varchar,
    PRIMARY KEY (user_group_id),
    FOREIGN KEY (created_by_id) REFERENCES users (user_id),
    FOREIGN KEY (archived_by_id) REFERENCES users (user_id)
);

CREATE TABLE IF NOT EXISTS user_groups_temp (
    user_group_id varchar,
    name varchar,
    description text,
    is_archived boolean,
    created_at timestamp,
    archived_at timestamp,
    created_by_id varchar,
    archived_by_id varchar
);

CREATE TYPE membership_action AS ENUM ('join', 'leave');

CREATE TABLE IF NOT EXISTS user_groups_membership_logs (
    membership_id varchar,
    user_group_id varchar,
    user_id varchar,
    action MEMBERSHIP_ACTION,
    "timestamp" timestamp,
    FOREIGN KEY (user_id) REFERENCES users (user_id),
    FOREIGN KEY (user_group_id) REFERENCES user_groups (user_group_id)
);

CREATE TABLE IF NOT EXISTS user_groups_membership_logs_temp (
    membership_id varchar,
    user_group_id varchar,
    user_id varchar,
    action MEMBERSHIP_ACTION,
    "timestamp" timestamp
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

CREATE TABLE IF NOT EXISTS mapping_sessions (
    project_id varchar,
    group_id varchar,
    user_id varchar,
    mapping_session_id bigserial unique,
    start_time timestamp DEFAULT NULL,
    end_time timestamp DEFAULT NULL,
    items_count int2 not null,
    PRIMARY KEY (project_id, group_id, user_id),
    FOREIGN KEY (project_id, group_id)
    REFERENCES groups (project_id, group_id),
    FOREIGN KEY (user_id)
    REFERENCES users (user_id)
);

CREATE TABLE IF NOT EXISTS mapping_sessions_results (
    mapping_session_id int8,
    task_id varchar,
    result int2 not null,
    PRIMARY KEY (mapping_session_id, task_id),
    FOREIGN KEY (mapping_session_id)
    references mapping_sessions (mapping_session_id)
);

CREATE TABLE IF NOT EXISTS mapping_sessions_results_geometry (
    mapping_session_id int8,
    task_id varchar,
    result geometry not null,
    PRIMARY KEY (mapping_session_id, task_id),
    FOREIGN KEY (mapping_session_id)
    references mapping_sessions (mapping_session_id)
);

CREATE OR REPLACE FUNCTION mapping_sessions_results_constraint() RETURNS trigger
    LANGUAGE plpgsql AS
$$
DECLARE v mapping_sessions;
BEGIN
    IF NOT EXISTS(
        SELECT 1
        FROM tasks
        JOIN mapping_sessions ms
        ON ms.mapping_session_id = NEW.mapping_session_id
        WHERE tasks.task_id = NEW.task_id AND
            tasks.group_id = ms.group_id AND
            tasks.project_id = ms.project_id AND
            ms.mapping_session_id = NEW.mapping_session_id
        )
    THEN
        SELECT ms.project_id, ms.group_id, ms.user_id
        FROM mapping_sessions ms
        WHERE ms.mapping_session_id = NEW.mapping_session_id
        INTO v;
        RAISE EXCEPTION
        'Tried to insert invalid result: Project: % Group: % Task: % - User: %', v.project_id, v.group_id, NEW.task_id, v.user_id
            USING ERRCODE = '23503';
    END IF;
    RETURN NEW;
END;
$$;
CREATE TRIGGER insert_mapping_sessions_results BEFORE INSERT ON mapping_sessions_results
    FOR EACH ROW EXECUTE PROCEDURE mapping_sessions_results_constraint();

CREATE TRIGGER insert_mapping_sessions_results_geometry BEFORE INSERT ON mapping_sessions_results_geometry
    FOR EACH ROW EXECUTE PROCEDURE mapping_sessions_results_constraint();

-- Used to group results by user groups
CREATE TABLE IF NOT EXISTS mapping_sessions_user_groups (
    mapping_session_id int8,
    user_group_id varchar,  -- user group primary key
    PRIMARY KEY (mapping_session_id, user_group_id),
    FOREIGN KEY (mapping_session_id) REFERENCES mapping_sessions (mapping_session_id),
    FOREIGN KEY (user_group_id) REFERENCES user_groups (user_group_id)
);

-- create table for user_group_results import through csv
CREATE TABLE IF NOT EXISTS results_user_groups_temp (
    project_id varchar,
    group_id varchar,
    user_id varchar,
    user_group_id varchar
);
