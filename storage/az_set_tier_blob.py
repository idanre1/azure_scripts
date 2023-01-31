# pip install azure-cli
import re
from azure_env_crypt import aesCryptJson, az_cli, az_login

# argument parsing
import argparse
parser = argparse.ArgumentParser()
parser.add_argument("-a", "--account", action='store', type=str, required=True,   help="Storage account where container lives")
parser.add_argument("-c", "--container", action='store', type=str, required=True, help="Container name")
parser.add_argument("-p", "--path", action='store', type=str, default='',         help="sub path to blob container, working on full container if not set")
parser.add_argument("-f", "--from_tier", action='store', type=str, required=True, help="On which tiers to operate")
parser.add_argument("-t", "--to_tier", action='store', type=str, required=True,   help="Which tier to set: Hot, Cold, Archive")

args = parser.parse_args()
# Check login
az_login()

import os
sas_token=os.getenv('AZURE_STORAGE_SAS_TOKEN')
assert sas_token is not None, 'Error: credentials are not provided in EVN variable AZURE_STORAGE_SAS_TOKEN'

req=f'storage blob list --account-name {args.account} --container-name {args.container} --sas-token {sas_token}'
if args.path != '':
    req += f' --prefix {args.path}/'
res=az_cli(req)

select=[]
for f in res:
    if f['properties']['blobTier'] == args.from_tier:
        if f['properties']['blobType'] == 'BlockBlob':
            select.append(f['name'])

assert len(select) > 0, f'Error: No files were found answering path/from_tier creteria\nListing selected path files:\n{[(f["name"],f["properties"]["blobTier"]) for f in res]}'

print(f'Following file will change their tier to {args.to_tier}:')
print(select)
inp = input('Please confirm by typing "Yes": ')
assert inp == 'Yes', 'Cancelled'

req=f'storage blob set-tier --account-name {args.account} --container-name {args.container} --sas-token {sas_token}'
for f in select:
    print(f'Processing {f}')
    res=az_cli(f'{req} --name {f} --tier {args.to_tier}')
    assert res is not None, res

print('Done')

# storage blob list example (1 file in list):
# [
#   {
#     "container": "trydevops",
#     "content": "",
#     "deleted": null,
#     "encryptedMetadata": null,
#     "encryptionKeySha256": null,
#     "encryptionScope": null,
#     "hasLegalHold": null,
#     "hasVersionsOnly": null,
#     "immutabilityPolicy": {
#       "expiryTime": null,
#       "policyMode": null
#     },
#     "isAppendBlobSealed": null,
#     "isCurrentVersion": null,
#     "lastAccessedOn": null,
#     "metadata": {},
#     "name": "jukebox.service",
#     "objectReplicationDestinationPolicy": null,
#     "objectReplicationSourceProperties": [],
#     "properties": {
#       "appendBlobCommittedBlockCount": null,
#       "blobTier": "Hot",
#       "blobTierChangeTime": "2023-01-30T06:06:52+00:00",
#       "blobTierInferred": null,
#       "blobType": "BlockBlob",
#       "contentLength": 295,
#       "contentRange": null,
#       "contentSettings": {
#         "cacheControl": null,
#         "contentDisposition": null,
#         "contentEncoding": null,
#         "contentLanguage": null,
#         "contentMd5": "3CWHdWhoWevXTqQ/Ots4+g==",
#         "contentType": "text/x-dbus-service; charset=utf-8"
#       },
#       "copy": {
#         "completionTime": null,
#         "destinationSnapshot": null,
#         "id": null,
#         "incrementalCopy": null,
#         "progress": null,
#         "source": null,
#         "status": null,
#         "statusDescription": null
#       },
#       "creationTime": "2023-01-30T06:06:52+00:00",
#       "deletedTime": null,
#       "etag": "0x8DB02882E85750F",
#       "lastModified": "2023-01-30T06:06:52+00:00",
#       "lease": {
#         "duration": null,
#         "state": "available",
#         "status": "unlocked"
#       },
#       "pageBlobSequenceNumber": null,
#       "pageRanges": null,
#       "rehydrationStatus": null,
#       "remainingRetentionDays": null,
#       "serverEncrypted": true
#     },
#     "rehydratePriority": null,
#     "requestServerEncrypted": null,
#     "snapshot": null,
#     "tagCount": null,
#     "tags": null,
#     "versionId": null
#   }
# ]