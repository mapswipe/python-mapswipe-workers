
--  total_area & time_spent_max_allowed are maintaned and used by aggregated module
ALTER TABLE groups
    ADD COLUMN total_area float DEFAULT NULL,
    ADD COLUMN time_spent_max_allowed float DEFAULT NULL;
