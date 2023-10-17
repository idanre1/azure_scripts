import json

import argparse
parser = argparse.ArgumentParser(description='python handler example')
parser.add_argument('json_string', type=str, help='event result to process in json format (serialized)')
args = parser.parse_args()

result = json.loads(str(args.json_string))
print(result['eventType'])
print(result['data']['blobUrl'])

