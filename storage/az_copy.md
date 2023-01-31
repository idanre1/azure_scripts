# azcopy getting started
https://learn.microsoft.com/en-us/azure/storage/common/storage-use-azcopy-v10

# Copy a fileshare directory to another storage account
https://learn.microsoft.com/en-us/azure/storage/common/storage-use-azcopy-files#copy-a-directory-to-another-storage-account
```
azcopy copy 'https://<source-storage-account-name>.file.core.windows.net/<file-share-name>/<directory-path><SAS-token>' 'https://<destination-storage-account-name>.file.core.windows.net/<file-share-name><SAS-token>' --recursive
```
# Copy a blob directory to another storage account
https://learn.microsoft.com/en-us/azure/storage/common/storage-use-azcopy-blobs-copy
```
azcopy copy 'https://<source-storage-account-name>.blob.core.windows.net/<container-name>/<blob-path><SAS-token>' 'https://<destination-storage-account-name>.blob.core.windows.net/<container-name>/<blob-path><SAS-token>'
```