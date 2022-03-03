#https://stackoverflow.com/questions/61278034/copy-vhd-from-azure-disk-to-azure-storage-account

###################################################################################
# Config
###################################################################################

#Provide the subscription Id of the subscription where managed disk is created
subscriptionId="yourSubscriptionId"

#Provide the name of your resource group where managed is created
resourceGroupName="yourResourceGroupName"

#Provide the managed disk name 
diskName="yourVM-DiskName"

#Provide Shared Access Signature (SAS) expiry duration in seconds e.g. 3600.
#Know more about SAS here: https://docs.microsoft.com/en-us/Az.Storage/storage-dotnet-shared-access-signature-part-1
sasExpiryDuration="3600"

#Provide storage account name where you want to copy the underlying VHD of the managed disk. 
storageAccountName="yourstorageaccountName"

#Name of the storage container where the downloaded VHD will be stored
storageContainerName="yourstoragecontainername"

#Provide the name of the destination VHD file to which the VHD of the managed disk will be copied.
destinationVHDFileName="backup__${diskName}.vhd"

###################################################################################
# Execution
###################################################################################

# Set the context to the subscription Id where managed disk is created
az account set -s $subscriptionId

#Generate the SAS for the managed disk 
sasJson=`az disk grant-access -g $resourceGroupName -n $diskName --duration-in-seconds $sasExpiryDuration --access-level Read`
AccessSAS=$(echo $sasJson | python -c \
    'import json,sys;print json.load(sys.stdin)["accessSas"]')

# execute the copy
# not needed since az login should be used# --account-key "$storageAccountKey"
az storage blob copy start --account-name "$storageAccountName" \
--destination-blob "$destinationVHDFileName" --destination-container "$storageContainerName" \
--source-uri "$AccessSAS"

# show progress
sleep 5
az storage blob show --name $destinationVHDFileName --container-name $storageContainerName --account-name "$storageAccountName"
