#!/bin/bash
# Usage: <storage_account> <container> <local_path_to_archive> [Tier]

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

/usr/bin/rclone copy $PATH :azureblob:$CONTAINER --azureblob-account=$ACCOUNT --azureblob-sas-url $RCLONE_AZUREBLOB_SAS_URL --azureblob-access-tier=$TIER --copy-links $XXARGS -v
