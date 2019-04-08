-- noinspection SqlNoDataSourceInspectionForFile

CREATE TABLE IF NOT EXISTS projects (
    project_id varchar,
    name varchar,
    project_type int,
    project_details varchar,
    group_average int,
    contributors int,
    image varchar,
    is_featured boolean,
    look_for varchar,
    progress int,
    status varchar,
    verification_count int,
    archive boolean,
    project_type_specifics json,
    PRIMARY KEY(project_id)
    );

CREATE TABLE IF NOT EXISTS groups (
    project_id varchar,
    group_id int,
    number_of_tasks int,
    completed_count int,
    verification_count int,
    project_type_specifics json,
    PRIMARY KEY(project_id, group_id),
    FOREIGN KEY (project_id) REFERENCES projects (project_id)
    );

CREATE INDEX groups_projectid ON public.groups USING btree (group_id);
CREATE INDEX groups_goupid ON public.groups USING btree (project_id);

CREATE TABLE IF NOT EXISTS tasks (
    project_id varchar,
    group_id int,
    task_id varchar,
    project_type_specifics json,
    PRIMARY KEY(project_id, group_id, task_id),
    FOREIGN KEY (project_id) REFERENCES projects (project_id),
    FOREIGN KEY (project_id, group_id) REFERENCES groups (project_id, group_id)
    );

CREATE INDEX tasks_task_id ON public.tasks USING btree (task_id);
CREATE INDEX tasks_groupid ON public.tasks USING btree (group_id);
CREATE INDEX tasks_projectid ON public.tasks USING btree (project_id);

CREATE TABLE IF NOT EXISTS users (
    user_id varchar,
    username varchar,
    contribution_count int,
    distance double precision,
    PRIMARY KEY(user_id)
    );

CREATE TABLE IF NOT EXISTS results (
    project_id varchar,
    group_id int,
    user_id varchar,
    task_id varchar,
    "timestamp" bigint,
    result int,
    PRIMARY KEY (project_id, group_id, task_id, user_id),
    FOREIGN KEY (project_id) REFERENCES projects (project_id),
    FOREIGN KEY (project_id, group_id) REFERENCES groups (project_id, group_id),
    FOREIGN KEY (project_id, group_id, task_id) REFERENCES tasks (project_id, group_id, task_id),
    FOREIGN KEY (user_id) REFERENCES users (user_id)
    );

CREATE INDEX results_taskid ON public.results USING btree (task_id);
CREATE INDEX results_projectid ON public.results USING btree (project_id);
CREATE INDEX results_userid ON public.results USING btree (user_id);

CREATE TABLE IF NOT EXISTS progress(
    project_id int,
    contributors int,
    progress int,
    timestamp bigint,
    PRIMARY KEY (project_id)
    );
