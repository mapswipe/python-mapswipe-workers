FROM mdillon/postgis

COPY initdb.sql docker-entrypoint-initdb.d/
COPY serviceAccountKey.json serviceAccountKey.json

# Copy backup scripts and make them executable
COPY backup/make_basebackup.sh make_basebackup.sh
COPY backup/archive_command.sh archive_command.sh
RUN chmod +x make_basebackup.sh
RUN chmod +x archive_command.sh

# Install wal-g (used by backup/recovery scripts)
RUN apt-get update && apt-get install -y wget
RUN wget https://github.com/wal-g/wal-g/releases/download/v0.2.9/wal-g.linux-amd64.tar.gz
RUN tar -zxvf wal-g.linux-amd64.tar.gz
RUN mv wal-g /usr/local/bin/wal-g

# Do a basebackup of postgres every day
RUN echo "@daily bash /make_basebackup.sh" | crontab -
# Use following command to append job to cron
# CMD (crontab -l && echo "@daily bash ~/make_basebackup.sh") | crontab -
