#!/bin/bash
# Usage: rclone_sync.sh <storage_account> <container>[/remote_path] <path|file> [tier] [-i for interactive]
#        rclone_sync.sh <storage_account> <container> . Hot --exclude .git/

# https://forum.rclone.org/t/can-rclone-be-run-solely-with-command-line-options-no-config-no-env-vars/6314/5
ACCOUNT=$1
CONTAINER=$2
PATH=$3

if [ $# -eq 3 ]; then
    TIER='Hot' #,Cool,Archive
    XXARGS=''
elif [ $# -ge 4 ]; then
    TIER=$4 # Hot,Cool,Archive
    XXARGS=${@:5}
else
    echo "Arguments mismatch"
    exit
fi

echo "Selected Tier: $TIER"
if [ "$TIER" = 'Archive' ]; then
    echo "*** WARNING: You selected archive, please approve [Yes]"
    read approval
    if [ $approval != 'Yes' ]; then
        echo "*** Exiting"
        exit
    fi
fi

/usr/bin/rclone sync $PATH :azureblob:$CONTAINER --azureblob-account=$ACCOUNT --azureblob-sas-url $RCLONE_AZUREBLOB_SAS_URL --copy-links -v $XXARGS
