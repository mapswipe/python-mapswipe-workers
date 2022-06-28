-- DROP TABLE IF EXISTS results_user_groups_temp;
-- DROP TABLE IF EXISTS user_groups_temp;
-- DROP TABLE IF EXISTS user_groups_user_memberships_temp;
-- DROP TABLE IF EXISTS user_groups_user_memberships;
-- DROP TABLE IF EXISTS results_user_groups;
-- DROP TABLE IF EXISTS user_groups;

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
