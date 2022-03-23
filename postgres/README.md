# postgres continues backup to azure blob
https://thunderysteak.github.io/linux-mysql-azure-bck  
https://www.digitalocean.com/community/tutorials/how-to-set-up-continuous-archiving-and-perform-point-in-time-recovery-with-postgresql-12-on-ubuntu-20-04  

# manual install
1. open azure portal and create a new container
2. create rbac from rclone for the container  
`python <repo>/rclone/create_rclone_blob_container.py -r rg -a storageaccount -n postgres`
3. install_postgres_backup.sh storage--<backup_account_cred>--postgres.json <postgres_temp_PERSISTANT_path>
4. 
