# pip install azure-cli
from azure_env_crypt import aesCryptJson, az_cli, az_login
import json

# Check login
az_login()

# Using default subscription
res=az_cli('account list')
subscription=res[0]['id']
tenantId=res[0]['tenantId']

# --------------------------------------------------
# argument parsing
# --------------------------------------------------
import argparse
parser = argparse.ArgumentParser()
parser.add_argument("-r", "--rg", action='store', type=str, required=True,      help="Resource group for role")
parser.add_argument("-n", "--name", action='store', type=str, required=True,    help="App name for granting RBAC credentials")
parser.add_argument("-p", "--password", action='store', type=str, required=True,    help="aes password")
args = parser.parse_args()


# --------------------------------------------------
# Main
# --------------------------------------------------
# Creating custom rbac role with reduced privilages
# https://learn.microsoft.com/en-us/azure/role-based-access-control/role-definitions-list
# https://nicolgit.github.io/nicoltip032-how-can-authorize-to-turn-on-off-virtual-machine/

# load template
import pathlib
script_path=pathlib.Path(__file__).parent.resolve()
template = open(f'{script_path}/vm_start_stop.json', 'r').read()
cutsom_role=template.replace('__SUBSCRIPTION__', subscription)
with open('TEMP_vm_start_stop.json', 'w') as tmp_file:
	tmp_file.write(cutsom_role)

# create new role
res=az_cli('role definition create --role-definition TEMP_vm_start_stop.json')
if isinstance(res, dict):
	# {'id': '/subscriptions/abe7bbd2-f7ed-43cc-b936-4bf12801e734/providers/Microsoft.Authorization/roleDefinitions/ca0c193c-38da-4c71-a343-e052f75b604a', 'name': 'ca0c193c-38da-4c71-a343-e052f75b604a', 'type': 'Microsoft.Authorization/roleDefinitions', 'roleName': 'Virtual Machine User (Read/Start/Stop)', 'description': 'Can deallocate, start  and restart virtual machines.', 'roleType': 'CustomRole', 'permissions': [{'actions': ['Microsoft.Compute/*/read', 'Microsoft.Compute/virtualMachines/start/action', 'Microsoft.Compute/virtualMachines/restart/action', 'Microsoft.Compute/virtualMachines/deallocate/action'], 'notActions': [], 'dataActions': [], 'notDataActions': []}], 'assignableScopes': ['/subscriptions/abe7bbd2-f7ed-43cc-b936-4bf12801e734']}
	name=res['name']
else:
	# role already exists
	role_name = json.loads(cutsom_role)['Name']
	res=az_cli(f'role definition list -n {role_name.replace(" ","#")}')
	#[{'id': '/subscriptions/abe7bbd2-f7ed-43cc-b936-4bf12801e734/providers/Microsoft.Authorization/roleDefinitions/78e0d9ba-ae23-4003-8508-74ef3263a20c', 'name': '78e0d9ba-ae23-4003-8508-74ef3263a20c', 'type': 'Microsoft.Authorization/roleDefinitions', 'roleName': 'Virtual Machine User (Read/Start/Stop)', 'description': 'Can deallocate, start  and restart virtual machines.', 'roleType': 'CustomRole', 'permissions': [{'actions': ['Microsoft.Compute/*/read', 'Microsoft.Compute/virtualMachines/start/action', 'Microsoft.Compute/virtualMachines/restart/action', 'Microsoft.Compute/virtualMachines/deallocate/action'], 'notActions': [], 'dataActions': [], 'notDataActions': []}], 'assignableScopes': ['/subscriptions/abe7bbd2-f7ed-43cc-b936-4bf12801e734']}]
	assert isinstance(res, list), "Returned error on existing role name"
	name=res[0]['name']

# Found role ID
print(f'Role ID is: {name}')

# remove temp files
pathlib.Path('TEMP_vm_start_stop.json').unlink()

# assign SP to role
Json_create=az_cli(f'ad sp create-for-rbac -n {args.name} --role {name} --scopes /subscriptions/{subscription}/resourceGroups/{args.rg}')
appId=Json_create["appId"]
password=Json_create["password"]

# dump to JSON
dump={
	'appId':appId,
	'password':password,
}
aes=aesCryptJson(f'{args.name}.aes', args.password)
aes.encrypt(dump)
print('Credentials file: %s.aes' % args.name)

