#!/bin/bash
# Usage: rclone_sync.sh <storage_account> <container> <path> [-i for interactive]

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

/usr/bin/rclone sync $PATH :azureblob:$CONTAINER --azureblob-account=$ACCOUNT --copy-links $XXARGS
