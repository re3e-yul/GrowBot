#!/bin/bash
MinNow=$(date +%M)
MinStop=$(echo 'scale=1; 1 + ' $MinNow | bc)
date
while [ $(date +%M) -lt $MinStop ]
do
	gpio -g write 14 1
	./pH.py
	sleep 4
done
gpio -g write 14 0
echo "Done"
