import anyio
import asyncclick as click
import logconfig
import yaml
import os
import sys
import mqtt
import asyncio
from TLScontext import TLScontext
import ssl
from asyncio_mqtt import MqttError
import time

LOG = logconfig.init_logging("obu")
#using click to specify the configfile with all config details, using built in function in click to verify that file exist
@click.command()
@click.option("-config", help="Path to configfile", required=True, type=click.Path(exists=True))

async def main(config):

    try:
        with open(config,'r') as f:
            cfg = yaml.safe_load(f) #Open file and load content to cfg
    except yaml.scanner.ScannerError as e:
        LOG.error("Error reading file: {}".format(config))
        sys.exit(1)    
    #create TLScontext, passing the paths to the files stated in the configfile
    context =  TLScontext.create_tls_context(ca_certs=cfg["ca_cert"], 
        certfile=cfg["certfile"], 
        keyfile=cfg["keyfile"], 
        cert_reqs=ssl.CERT_REQUIRED)

    while True: #Run until it stops
        try:
            await mqtt.handler(mqtt_hostname=cfg["MQTT_URL"],
                mqtt_port=cfg["MQTT_port"],
                logger=LOG,
                context=context,
                topics=cfg["Topics"],
                router=cfg["4GRouter"])
        except MqttError as error:
            print(f'Error "{error}". Reconnecting in seconds.')
            await asyncio.sleep(1)     

#if __name__ == "__main__":
asyncio.run(main(_anyio_backend="asyncio")) # pylint: disable=unexpected-keyword-arg
