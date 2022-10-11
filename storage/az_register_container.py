# pip install azure-cli
from azure_env_crypt import aesCryptJson, az_cli, az_login

# Check login
az_login()

# Using default subscription
res=az_cli('account list')
subscription=res[0]['id']
tenantId=res[0]['tenantId']

# argument parsing
import argparse
parser = argparse.ArgumentParser()
parser.add_argument("-r", "--rg", action='store', type=str, required=True,      help="Resource group for the storage account")
parser.add_argument("-a", "--account", action='store', type=str, required=True, help="Storage account where container lives")
parser.add_argument("-n", "--name", action='store', type=str, required=True,    help="Container name for granting RBAC credentials")

parser.add_argument("-p", "--password", action='store', type=str, required=True,help=".aes file password")
args = parser.parse_args()
name = f'storage--{args.account}--{args.name}'

# Creating rbac credentials
res=az_cli(f'ad sp create-for-rbac \
 --name {name} \
 --role Storage#Blob#Data#Contributor \
 --scopes /subscriptions/{subscription}/resourceGroups/{args.rg}/providers/Microsoft.Storage/storageAccounts/{args.account}/blobServices/default/containers/{args.name}')
appId=res['appId']
secret=res['password']

res=az_cli(f'role assignment create --assignee {appId} \
 --role Reader \
 --scope /subscriptions/{subscription}/resourceGroups/{args.rg}/providers/Microsoft.Storage/storageAccounts/{args.account}')

# Encrypting RBAC credentials
d = {}
d['AZURE_TENANT_ID']=tenantId
d['AZURE_CLIENT_ID']=appId
#d['AZURE_CLIENT_CERTIFICATE_PATH']=secret
d['AZURE_CLIENT_SECRET']=secret
aes=aesCryptJson(f'{name}.aes', args.password)
aes.encrypt(d)
print('Credentials file: %s.aes' % name)
