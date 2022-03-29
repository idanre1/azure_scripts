#!/bin/bash
# Check arguments
if [[ $# < 2 ]]; then
	echo "Usage: $0 <json_file> <db_path>"
	exit 1
fi

# conf file exists
if [[ ! -e $1 ]]; then
	echo "Error: json conf file $1 does not exists"
	exit 1
fi
JSON=$1
chmod 600 $JSON

# postgres persistant path exists
if [[ ! -d $2 ]]; then
    echo "Error: db_path $2 does not exists"
    exit 1
fi
DB_PATH=$2

# ---------------------------
# main
# ---------------------------
sudo mkdir $DB_PATH/database_archive_wal
sudo chown postgres:postgres $DB_PATH/database_archive_wal

sudo sh -c 'echo "idan regev 1" | python3 -c "import sys; txt=sys.stdin.read().strip(); print(f\"{sys.argv[1]}={chr(34)}{txt}{chr(34)}\")" ddd ' >> ddddd
