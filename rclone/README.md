# Install
- Use install script
- Register a storage account with SAS_URL
    -   `python ~/azure_scripts/storage/az_register_container.py -c container -a <storage_account> -n <.aes_file>`
# Usage
- Apply credentials
- `source ~/azure_scripts/env_from_aes_file.sh <.aes_file>`
- Try to ls a container
    - ~/azure_scripts/rclone/rclone_ls.sh <account> <container>