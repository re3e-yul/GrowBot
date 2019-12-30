gpio -g mode 5 out
gpio -g mode 6 out

valve=$1
Master=$(gpio -g read 5)
Dir=$(gpio -g read 6)
case $valve in
-f|-F|--feed)
	if [ $Dir -eq "0" ]
        then
		gpio -g write 5 0
        	sleep 0.5
		gpio -g write 6 1
		sleep 12
	else
		gpio -g write 5 1
	fi
  ;;
-c|-C|--cycle)
	if [ $Dir -eq "1" ]
        then
	        gpio -g write 5 0
		sleep 0.5
        	gpio -g write 6 0
		sleep 12
	else
                gpio -g write 5 1
	fi
  ;;
esac
gpio -g write 5 1
Master=$(gpio -g read 5)
Dir=$(gpio -g read 6)

if [ $Master -eq "0" ]
then 
	Master="On"
else 
	Master="Off"
fi
if [ $Dir -eq "0" ]
then 
        Dir="Cycle"
else 
        Dir="Feed"
fi
echo "Power: "$Master "  Dir: "$Dir
