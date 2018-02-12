#! /bin/bash
gpio -g mode 17 out
gpio -g mode 27 out

state=$(gpio -g read 17)
value=$(gpio -g read 27)

if [[ $value -eq "0" ]]
then
	if [[ $state -eq "0" ]]
	then
		gpio -g write 17 1
		gpio -g write 27 1
		echo "Enabled, Turned on"
	else
		gpio -g write 27 1
		echo "Turned on"
	fi

else
        gpio -g write 27 0 
 	echo "Turned off"
fi

