CREATE TABLE
    row_counts (
        relname text PRIMARY KEY,
        reltuples numeric
    );

CREATE OR REPLACE FUNCTION count_trig()
RETURNS TRIGGER AS
$$
   DECLARE
   BEGIN
   IF TG_OP = 'INSERT' THEN
      EXECUTE 'UPDATE row_counts set reltuples=reltuples +1 where relname = ''' || TG_RELNAME || '''';
      RETURN NEW;
   ELSIF TG_OP = 'DELETE' THEN
      EXECUTE 'UPDATE row_counts set reltuples=reltuples -1 where relname = ''' || TG_RELNAME || '''';
      RETURN OLD;
   END IF;
   END;
$$
LANGUAGE 'plpgsql';

CREATE OR REPLACE FUNCTION add_count_trigs()
RETURNS void AS
$$
   DECLARE
      rec   RECORD;
      q     text;
   BEGIN
      FOR rec IN SELECT relname
               FROM pg_class r JOIN pg_namespace n ON (relnamespace = n.oid)
               WHERE relkind = 'r' AND n.nspname = 'public' LOOP
         q := 'CREATE TRIGGER ' || rec.relname || '_count BEFORE INSERT OR DELETE ON ' ;
         q := q || rec.relname || ' FOR EACH ROW EXECUTE PROCEDURE count_trig()';
         EXECUTE q;
      END LOOP;
   RETURN;
   END;
$$
LANGUAGE 'plpgsql';

CREATE OR REPLACE FUNCTION init_row_counts()
RETURNS void AS
$$
   DECLARE
      rec   RECORD;
      crec  RECORD;
   BEGIN
      FOR rec IN SELECT relname
               FROM pg_class r JOIN pg_namespace n ON (relnamespace = n.oid)
               WHERE relkind = 'r' AND n.nspname = 'public' LOOP
         FOR crec IN EXECUTE 'SELECT count(*) as rows from '|| rec.relname LOOP
            -- nothing here, move along
         END LOOP;
         INSERT INTO row_counts values (rec.relname, crec.rows) ;
      END LOOP;

   RETURN;
   END;
$$
LANGUAGE 'plpgsql';
