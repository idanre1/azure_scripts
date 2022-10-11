#!/bin/sh
# Usage:
# args_to_aes_file.sh A=1 B=2

echo "*** Please enter filename:   "
read name
echo "*** Please enter password:   "
stty -echo
read password
stty echo

python $HOME/python_lib/azure_env_crypt/args_to_aes_file.py -f $name -p $password -d $@

