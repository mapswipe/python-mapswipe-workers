-- Import v1 MapSwipe data from csv to
-- the v2 MapSwipe database.
-- Make sure the v1 data is v2 conform
-- otherwise default to NULL value.

CREATE TEMP TABLE v1_projects (
    archive boolean,
    created timestamp DEFAULT NULL,
    contributor_count int DEFAULT NULL,
    image varchar,
    is_featured boolean,
    look_for varchar,
    name varchar,
    number_of_tasks int DEFAULT NULL,
    progress int,
    project_details varchar,
    project_id varchar,
    project_type int,
    result_count int DEFAULT NULL,
    status int,
    verification_number int DEFAULT NULL,
    project_type_specifics json,
    PRIMARY KEY(project_id)
);

\copy v1_projects(
    archive
    image,
    is_featured,
    look_for,
    name,
    progress,
    project_details,
    project_id,
    project_type,
    status,
    project_type_specifics
)
FROM 'export.csv'
WITH (FORMAT CSV, DELIMITER ',', HEADER TRUE);


