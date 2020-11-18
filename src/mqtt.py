import ssl
import logconfig
import time
import asyncio
import logging
from contextlib import AsyncExitStack, asynccontextmanager
from asyncio_mqtt import Client, MqttError
from ReadJSONRPC import teltonikaRUT9x
from ReadGPS import ColumbusV800

LOG = logging.getLogger("obu")

async def logSignal(router,interval):
    while True:
        #reads the signal strength at every interval
        router.readSignalStrength()
        await asyncio.sleep(interval)

async def sendPosition(client, pos,interval,topic):
    while True:
        t = time.time()
        #reads the position from the GPS
        position = pos.readGPS()
        #set up a set of asyncio tasks
        pubTasks = set()
        #loops through the positional data
        for x in position:
            # generate the topic
            top = topic + "/" + x
            message = position[x].__str__()
            #print(top + " : " + message)
            #create an asyncio task to publish to MQTT broker
            task = asyncio.create_task(client.publish(top,message,1))
            #add the task to the taskset
            pubTasks.add(task)
        #Run through all tasks in parallell opposed to in sequence.
        asyncio.gather(*pubTasks)
        #calculate how long time the loop shall sleep
        sleeptime = interval - (time.time() - t)
        await asyncio.sleep(sleeptime)

async def log_messages(messages, template):
    async for message in messages:
        # 🤔 Note that we assume that the message paylod is an
        # UTF8-encoded string (hence the `bytes.decode` call).
        print(template.format(message.payload.decode()))

async def cancel_tasks(tasks):
    for task in tasks:
        if task.done():
            continue
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass

async def handler(mqtt_hostname, mqtt_port, logger,context,topics,router):
    # defining an AsyncExitStack as stack to use with the asynccontextmanager
    async with AsyncExitStack() as stack:
        #set up a set of tasks the asyncio shall work through
        tasks = set()
        #defining what the asynccontextmanager shall do upon exit.
        stack.push_async_callback(cancel_tasks,tasks)
        #using the clientID as both clientID and base topic
        clientID = topics["clientID"]
        #TODO: Fix the asyncio_MQTT library with tuples to pass the certificates. 
        #initializing a MQTT client
        LOG.info("Connect to MQTT-broker")
        client = Client(mqtt_hostname,port=mqtt_port,logger=logger,tls_context=context,client_id=clientID)
        router = teltonikaRUT9x(router["hostname"],router["username"],router["password"])
        position = ColumbusV800()
        #putting the client into the asynccontextmanager
        await stack.enter_async_context(client)
        #Loop through all topics that we shall subscribe to
        topic_filters= topics["subscribe"]
        for topic_filter in topic_filters:
            #Use the filtered_messages to make an async generator 
            manager = client.filtered_messages(topic_filter)
            #put the generator into the asynccontextmanager 
            messages = await stack.enter_async_context(manager)
            template = f'[topic_filter="{topic_filter}"] {{}}'
            #set up a task 
            task = asyncio.create_task(log_messages(messages,template))
            tasks.add(task)
        #Make a list of topics with Qos 1 to feed into the client.subscribe
        subscribe_topics = []
        for i in topic_filters:
            subscribe_topics.append((i,1))
        await client.subscribe(subscribe_topics)
        
        #create a task that sends the position on the MQTT with the clientID as a basis for topic
        task = asyncio.create_task(sendPosition(client,position,0.2,clientID))
        tasks.add(task)
        #add the signallogging to the async tasks
        task = asyncio.create_task(logSignal(router,1))
        tasks.add(task)

        # Wait for everything to complete (or fail due to, e.g., network
        # errors)
        await asyncio.gather(*tasks)

