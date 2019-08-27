-- Export v1 MapSwipe data to csv.
-- Rename attributes to conform to v2.
\copy (
    SELECT archive
        image,
        isfeatured AS "is_featured",
        lookfor AS "look_for",
        name,
        progress,
        projectdetails AS "project_details",
        project_id,
        project_type,
        state AS "status",
        info AS "project_type_specifics"
    FROM projects
)
TO 'export.csv'
WITH (FORMAT CSV, DELIMITER ',', HEADER TRUE);
