#! /bin/bash
ReadSensor()
        {
	if [[ $1 == "-f" ]]
        then
                Mode="Flowering"
        elif [[ $1 == "-v" ]]
        then
                 Mode="Vegetative"
        fi
	pH=$(/var/www/Atlas-I2C.py 99 r)
        ECs=$(/var/www/Atlas-I2C.py 100 r)
	EC=$(echo "scale=3;" $(echo $ECs | awk -F "," '{print $1 }') "/ 1000" | bc )
        TDS=$(echo "scale=3;"$(echo $ECs | awk -F "," '{print $2 }')"/ 1000" | bc )
	Salt=$(echo $ECs | awk -F "," '{print $3 }')
        SG=$(echo $ECs | awk -F "," '{print $4 }')
	Mode=$(echo "select mode from farmdata ORDER BY date DESC LIMIT 1;" | mysql -upi -pa-51d41e Farm -N)
#	DayInMode=$(echo "select DayInMode from farmdata order by date desc limit 1;" | mysql -upi -pa-51d41e Farm -N)
	DayInMode=$(echo $((($(date +%s)-$(date +%s --date "2018-07-2"))/(3600*24))))
	if [[ $Mode="Flowering" ]]
        then
                TargetEC="2.400"
        elif [[ $Mode="Vegetative" ]]
        then
                TargetEC="1.800"
        fi
        TargetpH="5.8"
        DeltaEC=$(echo "scale=3;"$EC " - "$TargetEC | bc)
        DeltapH=$(echo "scale=3;"$pH " - "$TargetpH | bc)
	Level=$(echo "select Level from farmdata ORDER BY date DESC LIMIT 1;" | mysql -upi -pa-51d41e Farm -N)
	RTemp=$(echo "scale=2;$(cat /sys/bus/w1/devices/28-000006911175/w1_slave | awk -F 't=' '{ print $2}') / 1000 - 27.55" | bc)
	LTemp=$(echo "scale=2;$(cat /sys/bus/w1/devices/28-0000068f125a/w1_slave | awk -F 't=' '{ print $2}') / 1000" | bc)
	TTemp=$(echo "scale=2;$(cat /sys/bus/w1/devices/28-000007264b1a/w1_slave | awk -F 't=' '{ print $2}') / 1000" | bc)
	if [ $(gpio -g read 15) == "1" ]; then PumpStatus="Off";else PumpStatus="On";fi
        if [ $(gpio -g read 14) == "1" ]; then AirStatus="Off";else AirStatus="On";fi
	if [ $(gpio -g read 18) == "1" ]; then LigthStatus="Off";else LigthStatus="On";fi
        if [ $(gpio -g read 8) == "1" ];  then ExFan="Off";else ExFan="On";fi
        if [ $(/var/www/hall.py) == "0" ]; then Drain="Off";else Drain="On";fi

#       if [ $PumpStatus = "Off" ] && [ $Drain = "On" ]
#	then
#		Level=$(echo "scale=3;" $Level" - 1.47" | bc )
#       elif [ $PumpStatus = "On" ] && [ $Drain = "Off" ]
#	then
#		Level=$(echo "scale=3;"$Level "+ 1.51" | bc )
#       elif [ $PumpStatus = "On" ] && [ $Drain = "On" ]
#	then
#		Level=$(echo "scale=3;"$Level "+ 1.51" | bc )

	line=$(echo "'"$(date +%F-%H:%M:%S)"','"$LigthStatus"','"$ExFan"','"$AirStatus"','"$PumpStatus"','"$Drain"','"$Level"','"$Mode"','"$DayInMode"','"$LTemp"','"$RTemp"'")
	echo -e "INSERT INTO farmdata (date,lights,ExFan,AirPump,WaterPump,Drain,Level,mode,DayInMode,LampTemp,RoomTemp) VALUES ("$line ");"
        echo "INSERT INTO farmdata (date,lights,ExFan,AirPump,WaterPump,Drain,Level,mode,DayInMode,LampTemp,RoomTemp) VALUES ("$line ");" | mysql -upi -pa-51d41e Farm -N

	line=$(echo "'"$(date +%F-%H:%M:%S)"','"$TTemp"','"$pH"','"$DeltapH"','"$EC"','"$DeltaEC"','"$TDS"','"$Salt"','"$SG"'")
	echo -e "INSERT INTO H2O (date,Temp,pH,DpH,EV,DEV,TDS,Salt,SG) VALUES ("$line ");\n"
        echo "INSERT INTO H2O (date,Temp,pH,DpH,EV,DEV,TDS,Salt,SG) VALUES ("$line ");" | mysql -upi -pa-51d41e Farm -N
	
        }

while true
do
	ReadSensor $1
	sleep 5
done
