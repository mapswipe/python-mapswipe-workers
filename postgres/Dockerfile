FROM mdillon/postgis

COPY initdb.sql docker-entrypoint-initdb.d/
COPY serviceAccountKey.json serviceAccountKey.json
COPY stat_views.sql docker-entrypoint-initdb.d/
COPY scripts/wal-g/make_basebackup.sh make_basebackup.sh
COPY scripts/wal-g/archive_command.sh archive_command.sh
COPY scripts/wal-g/restore_command.sh restore_command.sh
RUN chmod +x make_basebackup.sh
RUN chmod +x archive_command.sh
RUN chmod +x restore_command.sh
# Do a basebackup of postgres every day
RUN echo "@daily bash ~/make_basebackup.sh" | crontab -
# Use following command to append job to cron
# CMD (crontab -l && echo "@daily bash ~/make_basebackup.sh") | crontab -
