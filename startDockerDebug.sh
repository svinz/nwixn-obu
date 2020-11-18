docker build -t obu:debug  --target debug .
echo "Time to run the debugger!!"
docker run --rm -it -p 5678:5678 --name debugger --network=host -v /home/pi/onboardunit/logs:/usr/src/app/logs:rw -v /home/pi/onboardunit/certs:/usr/src/app/certs:ro obu:debug 
