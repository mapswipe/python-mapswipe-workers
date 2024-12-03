/*
 * This script updates the `tasks` table by adjusting the following column:
 * - `geom`: Stores now not only polygon geometries but all geometry types (e.g. Point, LineString).
 *
 * Existing entries for `geom` are not affected by this change.
 *
 * The new street project type requires Point geometries to store the image location.
 *
 */


ALTER TABLE tasks ALTER COLUMN geom SET DATA TYPE geometry(Geometry, 4326);