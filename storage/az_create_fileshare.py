# pip install azure-cli
import re
from azure_env_crypt import aesCryptJson, az_cli, az_login

# argument parsing
import argparse
parser = argparse.ArgumentParser()
parser.add_argument("-a", "--account", action='store', type=str, required=True, help="Storage account where container lives")
parser.add_argument("-n", "--name", action='store', type=str, required=True,    help="Container name for granting RBAC credentials")
parser.add_argument("-m", "--mount_path", action='store', type=str, required=True,    help="Mount path to the fileshare")

args = parser.parse_args()
filename = f'storage--{args.account}--{args.name}.cred'

# Check mount
import os
USR=os.environ.get('USER')
msg=f'''
# How to create path correctly
sudo mkdir -p {args.mount_path}
sudo chown {USR} {args.mount_path}
'''
assert os.path.exists(args.mount_path), f"Mount does not exists\n{msg}"
assert len(os.listdir(args.mount_path)) == 0, f"Mount path is not empty\n{msg}"

# Check login
az_login()

# Using default subscription
res=az_cli('account list')
subscription=res[0]['id']
tenantId=res[0]['tenantId']

# Find key
res=az_cli(f'storage account keys list --account-name {args.account}')
# [
#   {
#     "creationTime": "2021-08-27T11:51:30.171586+00:00",
#     "keyName": "key1",
#     "permissions": "FULL",
#     "value": "pass1"
#   },
#   {
#     "creationTime": "2021-08-27T11:51:30.171586+00:00",
#     "keyName": "key2",
#     "permissions": "FULL",
#     "value": "pass2"
#   }
# ]
key = res[0]['value']

# Create file share
res=az_cli(f'storage share create --name {args.name} --account-name {args.account} --account-key "{key}"')
# {
#   "created": true
# }
assert "created" in res, "Result of creation is not true"
assert res['created']
print(f'File share created.')

with open(filename, 'w') as f:
    f.write(f'username={args.account}\n')
    f.write(f'password={key}')
print(f'Credentails file:{filename}')

# SMB stuff
res=az_cli(f'storage account show --name {args.account} --query primaryEndpoints.file')
httpEndpoint=res[6:] # Skip https: prefix
fileshare=f'{httpEndpoint}{args.name}'
credentialRoot="/etc/smbcredentials"

msg = f'''
#https://learn.microsoft.com/en-us/azure/storage/files/storage-how-to-use-files-linux?tabs=smb311
# How to mount:
sudo mkdir -p {credentialRoot}
sudo mv {filename} {credentialRoot}/
sudo chmod 600 {credentialRoot}/{filename}
sudo chown root /etc/smbcredentials/storage--finance1idan--data-registry.cred
# add to /etc/fstab:
if [ -z "$(grep {fileshare}\ {args.mount_path} /etc/fstab)" ]; then
    echo "{fileshare} {args.mount_path} cifs nofail,credentials={credentialRoot}/{filename},serverino,nosharesock,actimeo=30,uid={USR}" | sudo tee -a /etc/fstab > /dev/null
else
    echo "/etc/fstab was not modified to avoid conflicting entries as this Azure file share was already present. You may want to double check /etc/fstab to ensure the configuration is as desired."
fi
sudo mount -a
'''
print(msg)
