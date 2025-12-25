# pip install azure-storage-blob azure-identity tqdm
# https://learn.microsoft.com/en-us/azure/storage/blobs/storage-blob-python-get-started?tabs=sas-token

from pathlib import Path
from typing import Optional, Iterable
from glob import glob
from concurrent.futures import ThreadPoolExecutor, as_completed

from azure.identity import DefaultAzureCredential  # noqa: F401
from azure.storage.blob import BlobServiceClient, ContainerClient
from azure.core.exceptions import (
	ResourceExistsError,
	HttpResponseError,
	ResourceNotFoundError,
)
from tqdm import tqdm
from az_creds_util import get_az_creds


def get_blob_service_client_sas(account: str, sas_token: str) -> BlobServiceClient:
	account_url = f"https://{account}.blob.core.windows.net"
	# The SAS token string can be assigned to credential here or appended to the account URL
	credential = sas_token

	# Create the BlobServiceClient object
	blob_service_client = BlobServiceClient(account_url, credential=credential)
	return blob_service_client


def get_or_create_container(
	blob_service_client: BlobServiceClient, container_name: str
) -> ContainerClient:
	"""Get a ContainerClient, creating the container if it does not exist.

	If create_container fails due to permissions, log a warning and proceed
	assuming the container already exists or cannot be created.
	"""
	container_client = blob_service_client.get_container_client(container_name)
	try:
		container_client.create_container()
	except ResourceExistsError:
		# Container already exists, which is fine
		pass
	except HttpResponseError as e:
		print(
			f"Warning: could not create container '{container_name}' "
			f"(status {getattr(e, 'status_code', 'unknown')}): {e}"
		)
		# Proceed assuming limited permissions or pre-existing container
	return container_client


def _should_skip_existing(
	container_client: ContainerClient,
	blob_name: str,
	local_size: int,
) -> bool:
	"""
	Return True if a blob with the same name and size already exists.
	"""
	blob_client = container_client.get_blob_client(blob_name)
	try:
		props = blob_client.get_blob_properties()
	except ResourceNotFoundError:
		return False

	remote_size = getattr(props, "size", None)
	if remote_size is None:
		remote_size = getattr(props, "content_length", None)

	return remote_size == local_size


def upload_blob_file(
	blob_service_client: BlobServiceClient,
	container_name: str,
	filename: str,
	blob_name: Optional[str] = None,
	overwrite: bool = False,
	max_concurrency: int = 4,
) -> None:
	"""Upload a single file as one blob."""
	container_client = get_or_create_container(blob_service_client, container_name)
	path = Path(filename)

	if not path.is_file():
		raise ValueError(f"{filename} is not a file")

	if blob_name is None:
		blob_name = path.name

	file_size = path.stat().st_size

	# If not overwriting, skip when remote blob with same size already exists
	if not overwrite and _should_skip_existing(container_client, blob_name, file_size):
		print(
			f"Skipped existing file {filename} -> {blob_name} "
			f"(same size: {file_size} bytes)"
		)
		return

	with path.open(mode="rb") as data:
		try:
			container_client.upload_blob(
				name=blob_name,
				data=data,
				overwrite=overwrite,
				max_concurrency=max_concurrency,
			)
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


def _upload_one(
	container_client: ContainerClient,
	file_path: Path,
	blob_name: str,
	overwrite: bool,
	max_concurrency: int,
) -> None:
	# If not overwriting, skip when remote blob with same size already exists
	if not overwrite:
		local_size = file_path.stat().st_size
		if _should_skip_existing(container_client, blob_name, local_size):
			tqdm.write(
				f"Skipped existing blob {blob_name} "
				f"(same size: {local_size} bytes)"
			)
			return

	with file_path.open("rb") as data:
		container_client.upload_blob(
			name=blob_name,
			data=data,
			overwrite=overwrite,
			max_concurrency=max_concurrency,
		)


def upload_folder(
	blob_service_client: BlobServiceClient,
	container_name: str,
	path_pattern: str,
	prefix: Optional[str] = None,
	overwrite: bool = False,
	max_workers: int = 8,
	max_concurrency: int = 4,
) -> None:
	"""
	Upload content specified by a path or wildcard pattern into a container.

	Supported:
	- Single file path
	- Single folder path (recursively, with subfolders)
	- Wildcard patterns: *.ogg, **/*.ogg, etc.

	For folders, the virtual folder structure is preserved as blob names.
	If a prefix is given, it is prepended to each blob name inside the container.

	Parallelism:
	- Files are uploaded in parallel using ThreadPoolExecutor (max_workers).
	- Each blob upload uses Azure's internal parallelism (max_concurrency).
	"""
	container_client = get_or_create_container(blob_service_client, container_name)

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
				blob_name = (
					f"{prefix.rstrip('/')}/{relative}" if prefix else relative
				)
				uploads.append((file_path, blob_name))
		elif target_path.is_file():
			name = target_path.name
			blob_name = f"{prefix.rstrip('/')}/{name}" if prefix else name
			uploads.append((target_path, blob_name))
		else:
			print(f"Skipping non-existing path: {target_path}")

	if not uploads:
		raise ValueError(f"No files to upload for pattern: {path_pattern}")

	with ThreadPoolExecutor(max_workers=max_workers) as executor:
		future_to_blob = {
			executor.submit(
				_upload_one,
				container_client,
				file_path,
				blob_name,
				overwrite,
				max_concurrency,
			): blob_name
			for file_path, blob_name in uploads
		}

		with tqdm(
			total=len(future_to_blob), desc="Uploading files", unit="file"
		) as pbar:
			for future in as_completed(future_to_blob):
				blob_name = future_to_blob[future]
				pbar.set_description(f"Uploading {blob_name}")
				try:
					future.result()
					# _upload_one itself decides whether it uploaded or skipped
					# Here we just advance the overall counter
				except ResourceExistsError:
					tqdm.write(f"Skipped existing blob {blob_name}")
				except Exception as exc:
					tqdm.write(f"Error uploading {blob_name}: {exc}")
				pbar.update(1)


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
	parser.add_argument(
		"--workers",
		type=int,
		default=8,
		help="number of parallel file uploads (default: 8)",
	)
	parser.add_argument(
		"--max-concurrency",
		type=int,
		default=4,
		help="per-blob max_concurrency for Azure SDK (default: 4)",
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
		max_workers=args.workers,
		max_concurrency=args.max_concurrency,
	)
