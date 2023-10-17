# pip install azure-servicebus
#https://learn.microsoft.com/en-us/azure/event-grid/blob-event-quickstart-portal?toc=%2Fazure%2Fstorage%2Fblobs%2Ftoc.json#register-the-event-grid-resource-provider
#https://learn.microsoft.com/en-us/azure/service-bus-messaging/service-bus-python-how-to-use-queues?tabs=connection-string

import asyncio
from azure.servicebus.aio import ServiceBusClient

import json
with open('service_bus_cred.json') as fh:
    creds = json.load(fh)
    NAMESPACE_CONNECTION_STR = creds['NAMESPACE_CONNECTION_STR']
    QUEUE_NAME = creds['QUEUE_NAME']

async def run():
    # create a Service Bus client using the connection string
    async with ServiceBusClient.from_connection_string(
        conn_str=NAMESPACE_CONNECTION_STR,
        logging_enable=True) as servicebus_client:

        async with servicebus_client:
            # get the Queue Receiver object for the queue
            receiver = servicebus_client.get_queue_receiver(queue_name=QUEUE_NAME)
            async with receiver:
                received_msgs = await receiver.receive_messages(max_wait_time=500, max_message_count=20)
                for msg in received_msgs:
                    print("Received: " + str(msg))
                    # complete the message so that the message is removed from the queue
                    await receiver.complete_message(msg)

print('starting')
while True:
        print('Loop')
        asyncio.run(run())
print('done')
