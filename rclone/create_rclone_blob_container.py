# pip install azure-cli
from azure_env_crypt import az_cli, az_login
import json

# Check login
az_login()

# Using default subscription
res=az_cli('account list')
subscription=res[0]['id']
tenantId=res[0]['tenantId']

# argument parsing
import argparse
parser = argparse.ArgumentParser()
parser.add_argument("-r", "--rg", action='store', type=str, required=True,                help="Resource group for the storage account")
parser.add_argument("-a", "--account", action='store', type=str, required=True,           help="Storage account where container lives")
parser.add_argument("-n", "--container_name", action='store', type=str, required=True,    help="Container name for granting RBAC credentials")

args = parser.parse_args()
filename = f'storage--{args.account}--{args.container_name}.json'
display_name = f'{args.container_name}_rclone'

# Creating rbac credentials
res=az_cli(f'ad sp create-for-rbac \
 --name {display_name} \
 --role Storage#Blob#Data#Owner \
 --scopes /subscriptions/{subscription}/resourceGroups/{args.rg}/providers/Microsoft.Storage/storageAccounts/{args.account}/blobServices/default/containers/{args.container_name}')

# RBAC credentials to JSON
d = {}
d['appId']=res['appId']
d['name']=res['appId']
d['displayName']=display_name
d['password']=res['password']
d['tenant']=tenantId

print('Credentials file: %s' % filename)
with open(filename, "w") as out_file:
  json.dump(d, out_file, indent = 4)
