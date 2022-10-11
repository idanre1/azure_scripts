# pip install azure-cli
from azure.cli.core import get_default_cli
from azure_env_crypt import aesCryptJson
import json
debug=False
#https://aka.ms/azadsp-cli

def az_cli(args_str, verbose=True):
	import re
	'''
	Sign-in to azure if not already signed in from terminal
	'''
	# init
	jsondata=None

	# argument span
	args = f'{args_str} -o none'.split()
	args = [sub.replace('#', ' ') for sub in args] # When some argument needs spaces use '#' instead (# is comment in linux, thus a reasonable choice)
	if debug:
		print(args)
	
	# Invoke client
	cli = get_default_cli()
	res = cli.invoke(args)
	if cli.result.result:
		jsondata = cli.result.result
	elif cli.result.error:
		if verbose:
			#Please run 'az login' to setup account.
			print(cli.result.error)
		x = re.findall("Please run .az login. to setup account", str(cli.result.error))
		if len(x) > 0:
			raise EnvironmentError('AZ Login Error')

	# Return json result to main
	return jsondata       

# --------------------------------------------------
# Login
# --------------------------------------------------
try:
	# Check we already logged in
	az_cli('ad signed-in-user show', verbose=False)
	print('az already logged_in')
except EnvironmentError:
	print('az is not logged in, please perform manual login')
	az_cli('login --use-device-code')#, echo=True)

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
Json_create=az_cli(f'ad sp create-for-rbac -n {args.name} --role "{name}" --scopes /subscriptions/{subscription}/resourceGroups/{args.rg}')
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

