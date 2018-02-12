#!/bin/bash
gpio -g write 17 1
gpio -g write 15 1
StartDate=$(date +%T)
StopDate=$(date  "+%T" -d 6" minutes")
while [[ "$(date +%T)" -le "$StopDate" ]]
do
	sleep 2
	date +%T && echo $StopDate
done
echo $Statdate $StopDate
gpio -g write 15 0
gpio -g write 17 0
