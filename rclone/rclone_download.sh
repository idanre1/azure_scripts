#!/bin/bash
# Usage: <storage_account> <container> <remote path to download>
#        rclone_download.sh <storage_account> <container> . --exclude .git/

ACCOUNT=$1
CONTAINER=$2
PATH=$3
XXARGS=${@:4}

/usr/bin/rclone copy :azureblob:$CONTAINER/$PATH . --azureblob-account=$ACCOUNT --azureblob-sas-url $RCLONE_AZUREBLOB_SAS_URL --azureblob-access-tier=$TIER --copy-links -v $XXARGS
