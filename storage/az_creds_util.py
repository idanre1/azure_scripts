def _is_pyaescrypt_file(filepath):
	with open(filepath, 'rb') as f:
		header = f.read(3)
	return header == b"AES"

def get_az_creds(filename):
	if _is_pyaescrypt_file(filename):
		# Import repo only here to avoid dependency if not needed
		from azure_env_crypt import aesCryptJson
		
		# prompt for password
		from getpass import getpass
		password=getpass(prompt='Enter aes file password: ')

		# decrypt the file
		aes=aesCryptJson(filename, password)
		creds = aes.decrypt()
		sas_token = creds['AZURE_STORAGE_SAS_TOKEN']
	else:
		with open(filename) as fh:
			import json
			creds = json.load(fh)
			sas_token = creds['SAS_TOKEN']

	return sas_token