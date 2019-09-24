# Based on latest stable postgres.
FROM mdillon/postgis

# serviceAccountKey to access backup storage on Google Cloud Storage.
COPY serviceAccountKey.json serviceAccountKey.json

# Copy backup scripts and make them executable.
COPY wal-g/recovery.conf recovery.conf
COPY wal-g/restore_command.sh restore_command.sh
RUN chmod +x restore_command.sh

# Install wal-g (used by backup scripts).
RUN apt-get update && apt-get install -y wget
RUN wget https://github.com/wal-g/wal-g/releases/download/v0.2.9/wal-g.linux-amd64.tar.gz
RUN tar -zxvf wal-g.linux-amd64.tar.gz
RUN mv wal-g /usr/local/bin/wal-g

# Environment variables needed during build.
ARG WALG_GS_PREFIX
ARG GOOGLE_APPLICATION_CREDENTIALS

# Restore base backup.
RUN wal-g backup-fetch /var/lib/postgresql/restored-cluster LATEST
# Move recovery.conf to cluster to tell postgres where to fetch WAL from.
RUN mv recovery.conf /var/lib/postgresql/restored-cluster/recovery.conf
RUN chown -R postgres:postgres /var/lib/postgresql/restored-cluster/

# Environment variables needed during container runtime.
ENV WALG_GS_PREFIX=$WALG_GS_PREFIX
ENV GOOGLE_APPLICATION_CREDENTIALS=$GOOGLE_APPLICATION_CREDENTIALS
ENV PGDATA var/lib/postgresql/restored-cluster
