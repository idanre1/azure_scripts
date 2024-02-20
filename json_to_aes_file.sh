#!/bin/sh
# Usage:
# json_to_aes_file.sh filename.json

if [ -e $1 ]; then
    echo ""
else
    echo "*** Error: json does not exists"
    exit
fi

ARGS=`python -c "import sys; import json; j=json.loads(sys.stdin.read()); s=''
for k,v in j.items(): s+=f'{k}={v} '
print(s)" < $1`

echo "*** Please enter filename:   "
read name
echo "*** Please enter password:   "
stty -echo
read password
stty echo


python $HOME/python_lib/azure_env_crypt/args_to_aes_file.py -f $name -p $password -d $ARGS

