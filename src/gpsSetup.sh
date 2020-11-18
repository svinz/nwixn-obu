
speed=$(stty -F /dev/ttyUSB0| awk '{print $2; exit}')
echo "Baud rate set up on tty Port:" $speed

if [ "$speed" -ne "38400" ]; then
    echo "Setting baud rate to 38400"
    stty -F /dev/ttyUSB0 38400
fi

#echo -e "\$PMTK220,200*2C\r\n" > /dev/ttyUSB0
echo "Attaching gps to gpsd"
gpsd /dev/ttyUSB0 -F /var/run/gpsd.sock
# echo "wait for 30s before sending command to gps"
# sleep 30
# echo "sending command to gps"
# gpsctl -c 0.2
