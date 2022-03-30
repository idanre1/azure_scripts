#!/bin/bash
# Check arguments
if [[ $# < 1 ]]; then
	echo "Usage: $0 <db_path>"
	exit 1
fi

# postgres persistant path exists
if [[ ! -d $1 ]]; then
    echo "Error: db_path $1 does not exists"
    exit 1
fi
DB_PATH=$1

# ---------------------------
# main
# ---------------------------
echo "*** Setup config"
sudo mkdir -p $DB_PATH/database_archive_wal
sudo mkdir -p $DB_PATH/database_backup
sudo chown postgres:postgres $DB_PATH/database_archive_wal $DB_PATH/database_backup

sudo sh -c "echo archive_mode = on >> /etc/postgresql/12/main/postgresql.conf"
sudo sh -c 'echo "test ! -f $0/database_archive_wal/%f && cp %p $0/database_archive_wal/%f" | python3 -c "import sys; txt=sys.stdin.read().strip(); print(f\"{sys.argv[1]}={chr(39)}{txt}{chr(39)}\")" archive_command >> /etc/postgresql/12/main/postgresql.conf' $DB_PATH

echo "*** Restarting postgres"
sudo systemctl restart postgresql@12-main

echo "*** Manual backup"
sudo -u postgres pg_basebackup -D $DB_PATH/database_backup

echo "*** Done"
