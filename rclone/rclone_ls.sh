#!/bin/sh
# Usage: rclone_ls.sh <storage_account> <container>

# https://forum.rclone.org/t/can-rclone-be-run-solely-with-command-line-options-no-config-no-env-vars/6314/5
ACCOUNT=$1
CONTAINER=$2

rclone ls :azureblob:$CONTAINER --azureblob-account=$ACCOUNT
