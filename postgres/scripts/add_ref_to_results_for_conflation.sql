ALTER TABLE mapping_sessions_results
ADD COLUMN ref jsonb;

ALTER TABLE results_temp
ADD COLUMN ref jsonb;
