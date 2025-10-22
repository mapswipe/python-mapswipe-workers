ALTER TABLE results_temp
ADD COLUMN ref jsonb;

ALTER TABLE results_geometry_temp
ADD COLUMN ref jsonb;

CREATE TABLE IF NOT EXISTS public.mapping_sessions_refs (
    mapping_session_id int8,
    task_id varchar,
    ref JSONB not null,
    PRIMARY KEY (mapping_session_id, task_id),
    FOREIGN KEY (mapping_session_id)
    references mapping_sessions (mapping_session_id)
);
