#!/bin/sh
# Usage: rclone_ls.sh <storage_account> <container>
#        rclone_ls.sh <storage_account> <container>[/remote_path]

# https://forum.rclone.org/t/can-rclone-be-run-solely-with-command-line-options-no-config-no-env-vars/6314/5
ACCOUNT=$1
CONTAINER=$2

rclone ls :azureblob:$CONTAINER --azureblob-account=$ACCOUNT --azureblob-sas-url $RCLONE_AZUREBLOB_SAS_URL
