-- noinspection SqlNoDataSourceInspectionForFile

CREATE TABLE IF NOT EXISTS projects (
  contributors int
  ,groupAverage int
  ,project_id int
  ,image varchar
  ,importKey varchar
  ,isFeatured boolean
  ,lookFor varchar
  ,name varchar
  ,progress int
  ,projectDetails varchar
  ,state int
  ,verificationCount int
  ,project_type int
  ,info json
  ,archive boolean

  ,CONSTRAINT projects_pkey PRIMARY KEY(project_id)
);

CREATE TABLE IF NOT EXISTS imports (
  import_id varchar
  ,info json

  ,CONSTRAINT imports_pkey PRIMARY KEY(import_id)
);

CREATE TABLE IF NOT EXISTS tasks (
  task_id varchar
  ,group_id int
  ,project_id int
  ,info json

  ,CONSTRAINT tasks_pkey PRIMARY KEY(task_id, group_id, project_id)
);

CREATE INDEX tasks_task_id ON public.tasks USING btree (task_id);
CREATE INDEX tasks_groupid ON public.tasks USING btree (group_id);
CREATE INDEX tasks_projectid ON public.tasks USING btree (project_id);

CREATE TABLE IF NOT EXISTS groups (
  project_id int
  ,group_id int
  ,count int
  ,completedCount int
  ,verificationCount int
  ,info json

  ,CONSTRAINT groups_pkey PRIMARY KEY(project_id, group_id)
);

CREATE INDEX groups_projectid ON public.groups USING btree (group_id);
CREATE INDEX groups_goupid ON public.groups USING btree (project_id);

CREATE TABLE IF NOT EXISTS users (
  user_id varchar
  ,contributions int
  ,distance double precision
  ,username varchar

  ,CONSTRAINT users_pkey PRIMARY KEY(user_id)
);

CREATE TABLE IF NOT EXISTS results (
  task_id character varying NOT NULL
  ,project_id integer NOT NULL
  ,user_id character varying NOT NULL
  ,"timestamp" bigint
  ,info json
  ,duplicates integer

  ,CONSTRAINT results_pkey PRIMARY KEY (task_id, user_id, project_id)
);
CREATE INDEX results_taskid ON public.results USING btree (task_id);
CREATE INDEX results_projectid ON public.results USING btree (project_id);
CREATE INDEX results_userid ON public.results USING btree (user_id);

CREATE TABLE IF NOT EXISTS progress(
  project_id int
  ,contributors int
  ,progress int
  ,timestamp bigint

);


