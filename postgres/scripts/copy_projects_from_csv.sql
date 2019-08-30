-- Import v1 MapSwipe data from csv to
-- the v2 MapSwipe database.
-- Make sure the v1 data is v2 conform
-- otherwise default to NULL value.
CREATE TEMP TABLE v1_projects(
    archive boolean,
    created timestamp DEFAULT NULL,
    contributor_count int DEFAULT NULL,
    image varchar,
    is_featured boolean,
    look_for varchar,
    name varchar,
    required_results int DEFAULT NULL,
    progress int,
    project_details varchar,
    project_id varchar,
    project_type int,
    result_count int DEFAULT NULL,
    status varchar,
    verification_number int DEFAULT NULL,
    project_type_specifics json
);

\copy v1_projects(archive, image, is_featured, look_for, name, progress, project_details, project_id, project_type, status, project_type_specifics) FROM 'projects.csv' WITH (FORMAT CSV, DELIMITER ',', HEADER TRUE);

-- Convert old status numbers (state) to new status string.
-- (Convert old to new data structure)
UPDATE v1_projects
SET status = 'active'
WHERE status = '0';

UPDATE v1_projects
SET status = 'inactive'
WHERE status = '3';

-- Insert or update data of temp table to the permant table (projects)
-- Note that the special excluded table is used to reference values originally proposed for insertion
INSERT INTO
  projects(
    archive,
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
SELECT
  archive,
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
FROM
  v1_projects
ON CONFLICT (project_id) DO UPDATE
SET
  archive = excluded.archive,
  name = excluded.name,
  progress = excluded.progress,
  status = excluded.status;
