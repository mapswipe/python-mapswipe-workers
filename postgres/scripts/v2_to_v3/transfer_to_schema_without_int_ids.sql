set search_path = without_int_id, public;

------------------------------------------------- projects -------------------------------------------------------------
Insert into without_int_id.projects (
    project_id,
    created,
    created_by,
    geom,
    image,
    is_featured,
    look_for,
    name,
    progress,
    project_details,
    project_type,
    required_results,
    result_count,
    status,
    verification_number,
    project_type_specifics
)
Select
    project_id,
    created,
    created_by,
    geom,
    image,
    is_featured,
    look_for,
    name,
    progress,
    project_details,
    project_type,
    required_results,
    result_count,
    status,
    verification_number,
    project_type_specifics
from public.projects;

------------------------------------------------- groups -------------------------------------------------------------
Insert into without_int_id.groups (
    project_id,
    group_id,
    number_of_tasks,
    finished_count,
    required_count,
    progress,
    project_type_specifics
)
select
    g.project_id,
    g.group_id,
    g.number_of_tasks,
    g.finished_count,
    g.required_count,
    g.progress,
    g.project_type_specifics

from public.groups g;

------------------------------------------------- tasks -------------------------------------------------------------
Insert into without_int_id.tasks (
    project_id,
    group_id,
    task_id,
    geom,
    project_type_specifics
)
select
    t.project_id,
    t.group_id,
    t.task_id,
    t.geom,
    t.project_type_specifics
from public.tasks t;

------------------------------------------------- users -------------------------------------------------------------
Insert into without_int_id.users (
    user_id,
    username,
    created
)
select
    user_id,
    username,
    created
from public.users;

------------------------------------------------- results -------------------------------------------------------------


INSERT INTO without_int_id.group_results (
    project_id,
    group_id,
    user_id,
    timestamp,
    session_length,
    result_count
)
    select
        project_id,
        group_id,
        user_id,
        timestamp,
        (end_time - start_time) as session_length,
        count(*) as result_count
    from
        public.results pr
    group by
        user_id,
        project_id,
        group_id,
        start_time,
        end_time,
        timestamp;

INSERT INTO without_int_id.results (
    result,
    task_id,
    result_id
)
    SELECT
        pr.result,
        pr.task_id,
        gr.result_id
    FROM public.results pr
    join
        group_results gr
    on
        gr.user_id = pr.user_id
    and gr.project_id = pr.project_id
    and gr.group_id = pr.group_id;