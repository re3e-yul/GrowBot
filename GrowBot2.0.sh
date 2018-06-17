#! /bin/bash

if [[ $# -eq 0 ]]
then
    echo "Usage: GrowBot6.sh -fF/-gG [Minutes period]"
    exit 0
fi
for var in "$@"
do
       case "$var" in
                -[fF]) Mode="Flowering"
                ;;
                -[gG]) Mode="Vegetative"
                ;;
                -[vV]) Mode="Vegetative"
                ;;
                [1-59]*) period=$var
                ;;
                -FF) ForceFlood="1"
        esac
case "$Mode" in
                Flowering)
                LightOn="08"
                LightOff="20"
                ;;
                Vegetative)
                LightOn="06"
                LightOff="22"
                ;;
esac
done
Level="0"
date=$(date +%T)
LastFlood=$(echo "SELECT LastFlood FROM farmSched ORDER BY date DESC LIMIT 1;" | mysql -upi -pa-51d41e Farm)
NextFlood=$(echo "SELECT NextFlood FROM farmSched ORDER BY date DESC LIMIT 1;" | mysql -upi -pa-51d41e Farm)




Lights()
        {
        #######################
        #                     #
        #  Turn on the lights #
        #                     #
        #######################
        LightOn=$1
        LightOff=$2
	period=$3
        if [ $(/bin/date +%H) -ge $LightOn ] && [ $(/bin/date +%H) -lt $LightOff ]
        then
#                echo "day"
                if [ $(gpio -g read 18) -eq 0 ]
                then
                        gpio -g write 18 1
                fi
		Water $period
        else
#                echo "night"
                if [ $(gpio -g read 18) -eq 1 ]
                then
                        gpio -g write 18 0
                fi
		Water $period
        fi
        
}

Water()
	{
	sensors=$ReadSensor
	Now=$(date +"%F %T")
	gw='gpio -g write'
	gr='gpio -g read'
	sql='mysql -upi -pa-51d41e Farm -N'
	Lr=$(if [[ $(gpio -g read 18) -eq "1" ]]; then  echo "Lights On"; else  echo "Lights Off"; fi)
	Pr=$(if [[ $(gpio -g read 15) -eq "1" ]]; then  echo "Water Pump On"; else  echo "Water Pump Off"; fi)
        Pw=$gw" 15"
	Poff=$Pw" 0"
	Pon=$Pw" 1"
        Fsched=$(echo "select * from farmSched order by date desc limit 1;" | mysql -upi -pa-51d41e Farm -N)
	if [[ -z $NextFlood ]]
	then
	        LastFlood=$(echo $Fsched | awk -F " " '{print $3 " " $4}')
	        NextFlood=$(echo $Fsched | awk -F " " '{print $5 " " $6}')
	fi
	period=$1
	FloodTime='5'
	if [[ $Now > $NextFlood ]]
	then
		in4=$(date +%T -d "+"$FloodTime"minutes")
		LastFlood=$(date +"%F %T")
		while [[ $(date +%T) < $in4 ]]
		do
			gpio -g write 15 1
			
			Pr=$(if [[ $(gpio -g read 15) -eq "1" ]]; then  echo "Water Pump On"; else  echo "Water Pump Off"; fi)
			Lr=$(if [[ $(gpio -g read 18) -eq "1" ]]; then  echo "Lights On"; else  echo "Lights Off"; fi)
			Sensor=$(ReadSensor)
			#echo -e "Now: "$(date +%T) "\n"$Lr"\n"$Pr "\ni'm fine, tkx, Next flood at: " $NextFlood "\n" # $(sensors | awk -F" " '{print $1"\n"$2"\n"$3"\n"$4"\n"$5"\n"$6"\n"$7"\n"$8"\n"$9}')
			clear && echo -e "Now: "$(date +%T) "\n"$Lr"\n"$Pr"\nstop at: "$in4 "\n" $Sensor
			sleep 1
		done
		gpio -g write 15 0
		NextFlood=$(date "+%F %T" --date='+'$period' minutes')
                LastpHCal=$(echo $Fsched | awk -F " " '{print $8 " " $9}')
                NextpHCal=$(echo $Fsched | awk -F " " '{print $10 " " $11}')
		Vol=$(echo $Fsched | awk -F " " '{print $12}')
                line=$(echo "'"$(date +"%F %T")"','"$LastFlood"','"$NextFlood"','"$period"','"$LastpHCal"','"$NextpHCal"','"$Vol"'")
# 		echo "line: " $line
		echo "INSERT INTO farmSched (date,LastFlood,NextFlood,period,LastpHCal,NextpHCal,Vol) VALUES ("$line ");" | mysql -upi -pa-51d41e Farm -N
		echo "select * from farmSched order by date desc limit 2;" | mysql -upi -pa-51d41e Farm -N
	else
		
		NextFlood=$(echo "select NextFlood from farmSched order by date desc limit 1;" | mysql -upi -pa-51d41e Farm -N)
		Pr=$(if [[ $(gpio -g read 15) -eq "1" ]]; then  echo "Water Pump On"; else  echo "Water Pump Off"; fi)
		Pr=$(if [[ $(gpio -g read 15) -eq "1" ]]; then  echo "Water Pump On"; else  echo "Water Pump Off"; fi)
		Sensor=$(ReadSensor)
		clear && echo -e "Now: "$(date +%T) "\n"$Lr"\n"$Pr "\ni'm fine, tkx, Next flood at: " $NextFlood "\n" $Sensor 
	fi 
	}


Aerate()
        {
        ####################################
        #                                  #
        #   air pump on/off even minutes   #
        #                                  #
        ####################################
        min=$(date +%M)
        if [ $((10#${min}%2)) -eq 0 ]
        then
#               gpio -g write 17 0
#               gpio -g write 15 1
                gpio -g write 14 1
        else
                gpio -g write 14 0
        fi

        #########################
        #                       #
        # rurn the exhaust fan  #
        #   3 min every hour    #
        #########################
        AirOut="56"
        ExFanStat=$(gpio -g read 8)
        #RoomTemp=$(for Tsens in $(ls -d /sys/bus/w1/devices/28-*); do echo 'scale=3;'$(cat $Tsens/w1_slave | tail -n 1 | awk -F"=" '{ print $2}') ' / 1000' | bc; done | head -n 1)
        if [[ $Tsens1 > 28.3 ]]
        then
                gpio -g write 8 1

        elif [[ $ExFanStat = 1 ]] && [[ $RoomTemp < 28.5 ]]
        then
                gpio -g write 8 0
#       else
#               gpio -g write 8 0
        fi

}



ReadSensor()
        {
        pH=$(/var/www/pH.py)
        ECs=$(/var/www/EC.py)
        EC=$(echo $ECs | awk -F " " '{print $1 }')
        TDS=$(echo $ECs | awk -F " " '{print $2 }')
        Salt=$(echo $ECs | awk -F " " '{print $3 }')
        SG=$(echo $ECs | awk -F " " '{print $4 }')
	Tsens2=$(echo "scale=3;$(for Tsens in $(ls -d /sys/bus/w1/devices/28-*); do cat $Tsens/w1_slave | tail -n 1 | awk -F"=" '{ print $2}'; done | head -n 1)/1000" |bc )
        Tsens1=$(echo "scale=3;$(for Tsens in $(ls -d /sys/bus/w1/devices/28-*); do cat $Tsens/w1_slave | tail -n 1 | awk -F"=" '{ print $2}'; done | tail -n 2 | head -n 1)/1000 - 12" | bc)
        Tsens3=$(echo "scale=3;$(for Tsens in $(ls -d /sys/bus/w1/devices/28-*); do cat $Tsens/w1_slave | tail -n 1 | awk -F"=" '{ print $2}'; done | tail -n 1)/1000" |bc)
        line=$(echo "'"$(date +%F-%H:%M:%S)"','"$Tsens3"','"$pH"','"$EC"','"$TDS"','"$Salt"','"$SG"'")
        echo "INSERT INTO H2O (date,Temp,pH,EV,TDS,Salt,SG) VALUES ("$line ");" | mysql -upi -pa-51d41e Farm -N
        sensors=$(echo -e $(date +%F-%H:%M:%S)"\n"$pH"\n"$EC"\n"$TDS"\n"$Salt"\n"$SG"\n"$Tsens2"\n"$Tsens1"\n"$Tsens3)
	}

while true 
do
	if [[ -z $(sudo ps -A | grep "readsensor.sh") ]]
        then
                /usr/bin/screen  -dm -S ReadSensors ~/readsensor.sh $Mode 
        fi
	Lights $LightOn $LightOff $period
	Aerate
	ReadSensor
done
