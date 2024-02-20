# azure_scripts
az cli and other azure scripts for fun
# Change a blob tier
```bash
python ~/azure_scripts/storage/az_set_tier_blob.py -a account -c container -p path/inner_dir -f Cool -t Cold
```
# Refresh SAS for storage blob
- Goto container in azure portal
- Generate SAS for specific blob
- Create a json file
```json
{
    "AZURE_STORAGE_SAS_TOKEN":"secret!"
}
```
- Encrypt it
```bash
~/azure_scripts/json_to_aes_file.sh file.json
```
- Delete the json file