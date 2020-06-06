#! /bin/bash

gpio -g mode 26 out
gpio -g mode 21 out
main=$(gpio -g read 26)
light=$(gpio -g read 21)
pump=$(gpio -g read 12)
fan=$(gpio -g read 16)
bubl=$(gpio -g read 20)

if [[ $light -eq 0 ]]
then
	if [[ $main -eq 0 ]]
	then
        	gpio -g write 26 1
	fi
	gpio -g write 21 1
elif [[ $light -eq 1 ]]
then
	gpio -g write 21 0
	if [[ $pump -eq 0 && $fan -eq 0 && $bubl -eq 0 ]]
        then
                gpio -g write 26 0
        fi
fi
sleep 0.5
main=$(gpio -g read 26)
light=$(gpio -g read 21)
echo -e "Main AC relay: " $main
echo -e "Light AC relay: "$light
