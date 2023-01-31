#!/bin/bash
# Usage: <storage_account> <container> <remote path to download>

ACCOUNT=$1
CONTAINER=$2
PATH=$3
XXARGS=${@:4}

/usr/bin/rclone copy :azureblob:$CONTAINER/$PATH . --azureblob-account=$ACCOUNT --azureblob-access-tier=$TIER --copy-links -v $XXARGS
