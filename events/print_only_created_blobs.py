import json
import re

import argparse
parser = argparse.ArgumentParser(description='python handler example')
parser.add_argument('json_string', type=str, help='event result to process in json format (serialized)')
parser.add_argument('--container', type=str, default='raw', help='default container name to listen to')
args = parser.parse_args()

result = json.loads(str(args.json_string))
event_type = result['eventType']

# Fetch filename
# https://crwar.blob.core.windows.net/raw/install_droplet.sh
raw_filename = result['data']['blobUrl']
comp_reg = re.compile(f"https.*?blob\.core\.windows\.net\/{args.container}\/(.*)")
filename = comp_reg.findall(raw_filename)[0]

# Type handler
if event_type == 'Microsoft.Storage.BlobDeleted':
    print(f'Deleted blob: {filename}')
elif event_type == 'Microsoft.Storage.BlobCreated':
    print(f'Ceated blob: {filename}')


