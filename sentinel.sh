#! /bin/bash
if [[  -z $(pgrep Grow) ]]
then
	sudo /usr/bin/screen  -dm -S Growbot /var/www/GrowBot2.0.sh -f 120
	sudo /usr/bin/screen  -dm -S Readsensor /var/www/readsensor.sh
	ScreenNum=$(sudo screen -ls | head -n 2)
	echo "executed deamon in" $ScreenNum
else
	ScreenNum=$(sudo screen -ls | head -n 2)
	echo "Process" $(pgrep Gr) "is already running in" $ScreenNum	
fi
