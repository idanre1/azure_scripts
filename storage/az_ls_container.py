# pip install azure-storage-blob azure-identity
#https://learn.microsoft.com/en-us/azure/storage/blobs/storage-blob-python-get-started?tabs=sas-token
# https://learn.microsoft.com/en-us/azure/storage/blobs/storage-blob-download-python

from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient

def get_blob_service_client_sas(account, sas_token: str):
	# TODO: Replace <storage-account-name> with your actual storage account name
	account_url = f"https://{account}.blob.core.windows.net"
	# The SAS token string can be assigned to credential here or appended to the account URL
	credential = sas_token

	# Create the BlobServiceClient object
	blob_service_client = BlobServiceClient(account_url, credential=credential)

	return blob_service_client

def list_blobs_flat(blob_service_client: BlobServiceClient, container_name):
    container_client = blob_service_client.get_container_client(container=container_name)

    blob_list = container_client.list_blobs()

    for blob in blob_list:
        print(f"Name: {blob.name}")

if __name__ == "__main__":
	import argparse
	parser = argparse.ArgumentParser(description='Download file to remote server')
	parser.add_argument('account', type=str, help='storage account')
	parser.add_argument('container', type=str, help='container name')
	parser.add_argument('creds', type=str, help='json credential file with SAS_TOKEN')
	args = parser.parse_args()

	with open(args.creds) as fh:
		import json
		creds = json.load(fh)
		sas_token = creds['SAS_TOKEN']

	blob_service_client = get_blob_service_client_sas(args.account,sas_token)
	list_blobs_flat(blob_service_client, args.container)



