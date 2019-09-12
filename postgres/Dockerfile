FROM postgres
COPY initdb.sql /docker-entrypoint-initdb.d/
WORKDIR ~
COPY wal-g/make_basebackup.sh make_basebackup.sh
COPY wal-g/archive_command.sh archive_command.sh
COPY wal-g/restore_command.sh restore_command.sh
CMD chmod +x make_basebackup.sh
CMD chmod +x archive_command.sh
CMD chmod +x restore_command.sh
# Do a basebackup of postgres every day
CMD (crontab -l && echo "@daily bash ~/make_basebackup.sh") | crontab -
