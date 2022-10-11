#!/bin/sh

echo "*** Exporting environment variables"
echo "*** Please enter password:   "
stty -echo
read password
stty echo
python $HOME/python_lib/azure_env_crypt/json_from_aes_file.py -f $1 -p $password

