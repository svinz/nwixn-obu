import subprocess
import gpsd
import time
import logging
LOG = logging.getLogger("obu")

class ColumbusV800:
    def __init__(self):
        # #check if we are running inside a docker container
        # if in_docker():
        #     #ensure GPS have correct baudrate and is attached
        #     subprocess.call(["sh", "src/gpsSetup.sh"])
        # else:
        #     #ensure GPS have correct baudrate and is attached
        #     subprocess.call(["sudo","sh", "src/gpsSetup.sh"])

        # # set the gps to 5Hz interval
        # subprocess.call(["gpsctl","-c","0.2"])
        # Connect to the GPS
        LOG.info("Connect to gpsd on the host machine")
        gpsd.connect()
    
    def readGPS(self):
        # get the gpsd json
        packet = gpsd.get_current()
        # retrieve position
        pos = packet.position()
        # retrieve altitude
        alt = packet.altitude()
        # retrieve GPS time
        tid = packet.get_time()
        # retrieve speed
        speed = packet.speed()
        #set up an empty dict
        result = {}
        
        result["location"] = pos[0].__str__() +","+ pos[1].__str__()
        result["alt"] = alt
        result["speed"] = speed
        result["GPStimestamp"] = tid.__str__()
        LOG.info(result)
        return result

#Collected from:
#https://stackoverflow.com/questions/20010199/how-to-determine-if-a-process-runs-inside-lxc-docker
def in_docker():
    """ Returns: True if running in a Docker container, else False """
    with open('/proc/1/cgroup', 'rt') as ifh:
        return 'docker' in ifh.read()


