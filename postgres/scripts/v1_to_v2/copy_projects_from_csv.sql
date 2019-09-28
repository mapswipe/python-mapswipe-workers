-- Import v1 MapSwipe data from csv to
-- the v2 MapSwipe database.
-- Make sure the v1 data is v2 conform
-- otherwise default to NULL value.
CREATE TEMP TABLE v1_projects(
    archive boolean,
    contributor_count int DEFAULT NULL,
    created timestamp DEFAULT NULL,
    geom geometry(MULTIPOLYGON,4326) DEFAULT NULL,
    image varchar,
    import_id varchar,
    is_featured boolean,
    kml varchar DEFAULT NULL,
    look_for varchar,
    name varchar,
    progress int,
    project_details varchar,
    project_id varchar,
    project_type int,
    required_results int DEFAULT NULL,
    result_count int DEFAULT NULL,
    status varchar,
    verification_number int DEFAULT NULL,
    project_type_specifics json
);

CREATE TEMP TABLE v1_imports(
    import_id varchar,
    info json,
    kml varchar DEFAULT NULL
);

\copy v1_projects(archive, image, import_id, is_featured, look_for, name, progress, project_details, project_id, project_type, status, project_type_specifics) FROM projects.csv WITH (FORMAT CSV, DELIMITER ',', HEADER TRUE);

\copy v1_imports(import_id, info) FROM imports.csv WITH (FORMAT CSV, DELIMITER ',', HEADER TRUE);

-- Convert old status numbers (state) to new status string.
-- (Convert old to new data structure)
UPDATE v1_projects
SET status = 'active'
WHERE status = '0';

UPDATE v1_projects
SET status = 'inactive'
WHERE status = '3';

-- Extract geometry (kml) from info attribute (json) of imports table.
-- Get only the geometry (Polygone or MultiPolygon) of the kml string.
UPDATE v1_imports
SET kml = substring(info->'info'->>'kml' FROM '<Polygon>.*<\/Polygon>|<MultiPolygon>.*<\/MultiPolygon>');

UPDATE v1_projects
SET kml = v1_imports.kml
FROM v1_imports
WHERE v1_projects.import_id = v1_imports.import_id;

-- Convert geometry to postgis geometry type.
-- If Geoemtry is invalid (Exception gets raised)
-- Do Nothing. Continue with the next project.
do $$
DECLARE
    r record;
BEGIN
    -- record is a structure that contains an element for each column in the select list
    FOR r IN SELECT * from v1_projects
    LOOP
        BEGIN
            UPDATE v1_projects
            SET geom = ST_Force2D(ST_Multi(ST_GeomFromKML(kml)))
            WHERE v1_projects.project_id = r.project_id;
            -- note the where condition that uses the value from the record variable
        EXCEPTION
            WHEN OTHERS THEN
            -- do nothing
            END;
    END LOOP;
END
$$ LANGUAGE plpgsql;

-- Insert or update data of temp table to the permant table (projects)
-- Note that the special excluded table is used to reference values originally proposed for insertion
INSERT INTO
  projects(
    archive,
    geom,
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
  geom,
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
