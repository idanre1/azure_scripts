#!/bin/bash
# Create log analytics and save to aes
# https://trstringer.com/systemd-journal-to-syslog-azure-monitoring/
# cmd.sh <resource_group> <logs_workspace_name>

# install on linux client:
# wget https://raw.githubusercontent.com/Microsoft/OMS-Agent-for-Linux/master/installer/scripts/onboard_agent.sh && sh onboard_agent.sh -w $WORKSPACE_ID -s $WORKSPACE_KEY -d opinsights.azure.com

RG=$1
NAME=$2

echo "*** Creating logs workspace"
#az monitor log-analytics workspace create --resource-group $RG --workspace-name $NAME

WORKSPACE_ID=`az monitor log-analytics workspace show --resource-group $RG --workspace-name $NAME --query customerId -o tsv`
WORKSPACE_KEY=`az monitor log-analytics workspace get-shared-keys --resource-group $RG --workspace-name $NAME --query primarySharedKey -o tsv`

/nas/azure-env-crypt/args_to_aes_file.sh WORKSPACE_ID=$WORKSPACE_ID WORKSPACE_KEY=$WORKSPACE_KEY
