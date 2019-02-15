#! /bin/bash
now=$(date  "+%T")
StopTime=$(date  "+%T" -d "4 minutes")
gpio -g write 15 1
while [[ "$now" < "$StopTime" ]]
do
	now=$(date  "+%T")
	clear
	echo $now "Waiting until " $StopTime
	./pH.py
	./EC2.py
	echo "Gpio 15: " $(gpio -g read 15)
	sleep 3
done
gpio -g write 15 0
echo "Gpio 15: " $(gpio -g read 15)
echo "Done"
