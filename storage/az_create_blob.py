# pip install azure-cli
import re
from azure_env_crypt import aesCryptJson, az_cli, az_login

# argument parsing
import argparse
parser = argparse.ArgumentParser()
parser.add_argument("-a", "--account", action='store', type=str, required=True, help="Storage account where container lives")
parser.add_argument("-s", "--subscription", action='store', type=str, default='', help="Which subscription to handle")
parser.add_argument("-n", "--name", action='store', type=str, required=True,    help="Container name")
parser.add_argument("-p", "--password", action='store', type=str, default='',help=".aes file password")
# parser.add_argument("-t", "--tier", action='store', type=str, default='TransactionOptimized', help="Hot, Cold")

args = parser.parse_args()
filename = f'storage--{args.account}--{args.name}.aes'

# Check for valid password
if args.password == '':
    from getpass import getpass
    password=getpass(prompt='Enter aes file password: ')
else:
    password=args.password



# Check login
az_login()

res=az_cli('account list')
if args.subscription == '':
    # Using default subscription
    assert len(res) == 1, f"More than one subscription provided:{[s['name'] for s in res]}"
    subscription=res[0]['id']
    tenantId=res[0]['tenantId']
else:
    for i,s in enumerate(res):
        if args.subscription == s['name']:
            subscription=res[i]['id']
            tenantId=res[i]['tenantId']
print(f'Subscription:{subscription}')
print(f'TenantId:{tenantId}')

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

# Create container
res=az_cli(f'storage container create --name {args.name} --account-name {args.account} --account-key "{key}"')
# {
#   "created": true
# }
assert "created" in res, "Result of creation is not true"
assert res['created'], f'RAW Result: {res}'
print(f'Blob container created.')

# Generate account SAS
from datetime import datetime
# 1 year token
now = datetime.now()
expiry=f'{now.year+1}-{now.month}-{now.day}'

# https://learn.microsoft.com/en-us/cli/azure/storage/account?view=azure-cli-latest#az-storage-account-generate-sas
res=az_cli(f'storage account generate-sas --account-name {args.account} --account-key "{key}" --permissions cdlruwap --services b --resource-types sco --expiry {expiry}')
assert isinstance(res,str), f'az_cli returned a non-sas secret:\n{res}'

# credentials
# https://dvc.org/doc/command-reference/remote/modify
# export AZURE_STORAGE_SAS_TOKEN='mysecret'
d={}
d['AZURE_STORAGE_SAS_TOKEN']=res
aes=aesCryptJson(filename, password)
aes.encrypt(d)
print('Credentials file: %s' % filename)