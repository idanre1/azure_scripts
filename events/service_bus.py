# pip install azure-servicebus
#https://learn.microsoft.com/en-us/azure/event-grid/blob-event-quickstart-portal?toc=%2Fazure%2Fstorage%2Fblobs%2Ftoc.json#register-the-event-grid-resource-provider
#https://learn.microsoft.com/en-us/azure/service-bus-messaging/service-bus-python-how-to-use-queues?tabs=connection-string

import asyncio
from azure.servicebus.aio import ServiceBusClient

import json

import os
async def run(func, creds):
	# credentails
	with open(creds) as fh:
		creds = json.load(fh)
		NAMESPACE_CONNECTION_STR = creds['NAMESPACE_CONNECTION_STR']
		QUEUE_NAME = creds['QUEUE_NAME']

	# create a Service Bus client using the connection string
	async with ServiceBusClient.from_connection_string(
		conn_str=NAMESPACE_CONNECTION_STR,
		logging_enable=True) as servicebus_client:

		async with servicebus_client:
			# get the Queue Receiver object for the queue
			receiver = servicebus_client.get_queue_receiver(queue_name=QUEUE_NAME)
			async with receiver:
				received_msgs = await receiver.receive_messages(max_wait_time=5000, max_message_count=20)
				for msg in received_msgs:
					# print("Received: " + str(msg))
					result = json.loads(str(msg))
					os.system(f'''python {func} '{json.dumps(result)}' ''')
					# print(result['eventType'])
					# print(result['data']['blobUrl'])
					# complete the message so that the message is removed from the queue
					await receiver.complete_message(msg)

if __name__ == "__main__":
	import argparse
	parser = argparse.ArgumentParser(description='Handle events from azure storage')
	parser.add_argument('python_filename', type=str, default="print_only_created_blobs", help='python filename to execute when processing an event')
	parser.add_argument('--cred', type=str, default="service_bus_cred.json", help='credentials pile')
	args = parser.parse_args()

	print('starting')
	while True:
			print('Loop')
			asyncio.run(
				run(args.python_filename, args.cred)
				)
