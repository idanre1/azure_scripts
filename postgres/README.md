# postgres continues backup to azure blob
https://thunderysteak.github.io/linux-mysql-azure-bck  
https://www.digitalocean.com/community/tutorials/how-to-set-up-continuous-archiving-and-perform-point-in-time-recovery-with-postgresql-12-on-ubuntu-20-04  

# manual install
1. open azure portal and create a new fileshare at a storage account
<!-- 2. create rbac from rclone for the container  
`python <repo>/rclone/create_rclone_blob_container.py -r rg -a storageaccount -n postgres` -->
2. Assign file share
https://docs.microsoft.com/en-us/azure/storage/files/storage-how-to-use-files-linux?tabs=smb311
3. stop all db services, e.g.
`sudo systemctl stop matrix-synapse`
3. `install_postgres_backup.sh <postgres_temp_PERSISTANT_path>`
4. enable all db services, e.g.
`sudo systemctl start matrix-synapse`
