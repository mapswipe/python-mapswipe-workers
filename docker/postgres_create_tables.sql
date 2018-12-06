CREATE TABLE IF NOT EXISTS projects (
  project_id int
  ,project_type int
  ,name varchar
  ,objective varchar
  ,CONSTRAINT projects_pkey PRIMARY KEY(project_id)
);

CREATE TABLE IF NOT EXISTS tasks (
  task_id varchar
  ,group_id int
  ,project_id int
  ,info json
  ,CONSTRAINT tasks_pkey PRIMARY KEY(task_id, group_id, project_id)
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

