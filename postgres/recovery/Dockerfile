# Based on latest stable postgres.
FROM mdillon/postgis

COPY init_recovery.sh /usr/local/bin/
COPY restore_command.sh .
COPY recovery.conf .
COPY serviceAccountKey.json .

RUN chmod +x /usr/local/bin/init_recovery.sh
RUN chmod +x restore_command.sh

# Install wal-g (used by backup/restore scripts).
RUN apt-get update && apt-get install -y wget
RUN wget https://github.com/wal-g/wal-g/releases/download/v0.2.9/wal-g.linux-amd64.tar.gz
RUN tar -zxvf wal-g.linux-amd64.tar.gz
RUN mv wal-g /usr/local/bin/wal-g

# Restore base backup,
# set user permissions and
# copy recovery.conf into data cluster.
ENTRYPOINT ["init_recovery.sh"]
# Run default Postgres/PostGIS entrypoint and
# start Postgres.
CMD ["docker-entrypoint.sh", "postgres"]
