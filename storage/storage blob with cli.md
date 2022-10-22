# Install az
```bash
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash
```

# Login
`az login --use-device-code`

# List storage account
```bash
az storage account list \
--output table
```
# list account's containers
```bash
ACCOUNT=storage_account
az storage container list \
--account-name $ACCOUNT \
--output table
```
# ls for container
```bash
ACCOUNT=storage_account
CONTAINER=container
az storage blob list \
--container-name $CONTAINER \
--account-name $ACCOUNT \
--output table
```
# Upload to blob
```bash
CONTAINER=container
ACCOUNT=storage_account
KEY=secret
az storage blob upload \
--name data-registry \
--file "~/hello_world.py" \
--account-name $ACCOUNT \
--container-name $CONTAINER \
--account-key $KEY
```
# Use rbac instead of key
Replace `--account-key $KEY` with `--auth-mode login`
