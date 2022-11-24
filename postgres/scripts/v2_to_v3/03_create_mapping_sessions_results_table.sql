/*
 * This script introduces a new table called 'mapping_sessions_results'
 * which holds all the shared information of the results
 * of a single mapping session by a user.
 */
set search_path = 'public';

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

CREATE OR REPLACE TRIGGER insert_mapping_sessions_results BEFORE INSERT ON mapping_sessions_results
    FOR EACH ROW EXECUTE PROCEDURE mapping_sessions_results_constraint();
