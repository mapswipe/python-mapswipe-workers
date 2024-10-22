/*
 * This script updates the `mapping_sessions` table by adding the following columns:
 * - `app_version`: Stores the version of the client application.
 * - `client_type`: Indicates the type of client (currently supporting 'web' and 'mobile').
 * 
 * Existing entries for `app_version` and `client_type` will be set to an empty string
 * to indicate that they can correspond to either web or mobile, as web is already in use.
 * 
 * Related issue: https://github.com/mapswipe/mapswipe/issues/852#issuecomment-2400077760
 */


ALTER TABLE results_temp
    ADD COLUMN app_version varchar,
    ADD COLUMN client_type varchar;

ALTER TABLE results_geometry_temp
    ADD COLUMN app_version varchar,
    ADD COLUMN client_type varchar;

ALTER TABLE mapping_sessions
    ADD COLUMN app_version varchar,
    ADD COLUMN client_type varchar;
