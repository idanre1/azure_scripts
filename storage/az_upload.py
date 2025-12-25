# pip install azure-storage-blob azure-identity tqdm
# https://learn.microsoft.com/en-us/azure/storage/blobs/storage-blob-python-get-started?tabs=sas-token

from pathlib import Path
from typing import Optional, Iterable
from glob import glob

from azure.identity import DefaultAzureCredential  # noqa: F401
from azure.storage.blob import BlobServiceClient, ContainerClient
from azure.core.exceptions import ResourceExistsError
from tqdm import tqdm
from az_creds_util import get_az_creds


def get_blob_service_client_sas(account: str, sas_token: str) -> BlobServiceClient:
	account_url = f"https://{account}.blob.core.windows.net"
	# The SAS token string can be assigned to credential here or appended to the account URL
	credential = sas_token

	# Create the BlobServiceClient object
	blob_service_client = BlobServiceClient(account_url, credential=credential)
	return blob_service_client


def get_container(
	blob_service_client: BlobServiceClient, container_name: str
) -> ContainerClient:
	"""Get a ContainerClient, creating the container if it does not exist."""
	container_client = blob_service_client.get_container_client(container_name)
	# print error message if container does not exist
	# try:
	# 	container_client.get_container_properties()
	# except ResourceExistsError:
	# 	raise ValueError(f"Container does not exist: {container_name}")

	return container_client

def upload_blob_file(
	blob_service_client: BlobServiceClient,
	container_name: str,
	filename: str,
	blob_name: Optional[str] = None,
	overwrite: bool = False,
) -> None:
	"""Upload a single file as one blob."""
	container_client = get_container(blob_service_client, container_name)
	path = Path(filename)

	if not path.is_file():
		raise ValueError(f"{filename} is not a file")

	if blob_name is None:
		blob_name = path.name

	with path.open(mode="rb") as data:
		try:
			container_client.upload_blob(name=blob_name, data=data, overwrite=overwrite)
			print(f"Uploaded {filename} -> {blob_name}")
		except ResourceExistsError:
			print(f"Error: blob already exists {blob_name}")


def _expand_paths(pattern: str) -> Iterable[Path]:
	"""
	Expand a path pattern that may contain wildcards.

	If no wildcard characters are present, just return the single Path.
	If wildcards are present, use glob() to expand (recursive enabled for **).
	"""
	if any(ch in pattern for ch in "*?[]"):
		matches = [Path(p) for p in glob(pattern, recursive=True)]
		return matches
	return [Path(pattern)]


def upload_folder(
	blob_service_client: BlobServiceClient,
	container_name: str,
	path_pattern: str,
	prefix: Optional[str] = None,
	overwrite: bool = False,
) -> None:
	"""
	Upload content specified by a path or wildcard pattern into a container.

	Supported:
	- Single file path
	- Single folder path (recursively, with subfolders)
	- Wildcard patterns: *.ogg, **/*.ogg, etc.

	For folders, the virtual folder structure is preserved as blob names.
	If a prefix is given, it is prepended to each blob name inside the container.
	"""
	paths = list(_expand_paths(path_pattern))
	if not paths:
		raise ValueError(f"No paths matched: {path_pattern}")

	# Build a flat list of (local_path, blob_name) for tqdm
	uploads: list[tuple[Path, str]] = []

	for target_path in paths:
		if target_path.is_dir():
			base_path = target_path.resolve()
			for file_path in base_path.rglob("*"):
				if not file_path.is_file():
					continue
				relative = file_path.relative_to(base_path).as_posix()
				blob_name = f"{prefix.rstrip('/')}/{relative}" if prefix else relative
				uploads.append((file_path, blob_name))
		elif target_path.is_file():
			name = target_path.name
			blob_name = f"{prefix.rstrip('/')}/{name}" if prefix else name
			uploads.append((target_path, blob_name))
		else:
			print(f"Skipping non-existing path: {target_path}")

	if not uploads:
		raise ValueError(f"No files to upload for pattern: {path_pattern}")

	print(f"Uploading {len(uploads)} files to container '{container_name}'")

	container_client = get_or_create_container(blob_service_client, container_name)

	with tqdm(uploads, desc="Uploading files", unit="file") as pbar:
		for file_path, blob_name in pbar:
			# show file hierarchy in tqdm via blob_name (includes folders and prefix)
			pbar.set_description(f"Uploading {blob_name}")
			with file_path.open("rb") as data:
				try:
					container_client.upload_blob(
						name=blob_name,
						data=data,
						overwrite=overwrite,
					)
					tqdm.write(f"Uploaded {blob_name}")
				except ResourceExistsError:
					tqdm.write(f"Skipped existing blob {blob_name}")


if __name__ == "__main__":
	import argparse

	parser = argparse.ArgumentParser(
		description="Upload file, folder, or wildcard pattern to Azure Blob Storage"
	)
	parser.add_argument("account", type=str, help="storage account")
	parser.add_argument("container", type=str, help="container name")
	parser.add_argument("creds", type=str, help="json credential file with SAS_TOKEN")
	parser.add_argument(
		"path",
		type=str,
		help=(
			"file, folder, or wildcard pattern to upload "
			"(e.g. /tmp/data, /tmp/data/*.ogg, /tmp/data/**/*.parquet)"
		),
	)
	parser.add_argument(
		"--prefix",
		type=str,
		default=None,
		help="optional prefix (virtual folder) inside the container",
	)
	parser.add_argument(
		"--overwrite",
		action="store_true",
		help="overwrite existing blobs",
	)
	args = parser.parse_args()

	sas_token = get_az_creds(args.creds)
	blob_service_client = get_blob_service_client_sas(args.account, sas_token)

	# Single entry point: upload_folder handles file, folder, and wildcard patterns
	upload_folder(
		blob_service_client,
		args.container,
		args.path,
		prefix=args.prefix,
		overwrite=args.overwrite,
	)
