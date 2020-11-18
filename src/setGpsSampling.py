import subprocess

    # set the gps to 5Hz interval
subprocess.call(["gpsctl","-c","0.2"])