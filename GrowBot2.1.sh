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
                [1-999]*) period=$var   
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
                if [ $(gpio -g read 18) -eq 0 ]
                then
                        gpio -g write 18 1
                fi
        else
                if [ $(gpio -g read 18) -eq 1 ]
                then
                        gpio -g write 18 0
                fi
        fi
}

Water()
	{
	Mode=$1
	period=$2
	Now=$(date +"%F %T")
        Fsched=$(echo "select * from farmSched order by date desc limit 1;" | mysql -upi -pa-51d41e Farm -N)
        LastFlood=$(echo $Fsched | awk -F " " '{print $3 " " $4}')
        NextFlood=$(echo $Fsched | awk -F " " '{print $5 " " $6}')
	LastpHCal=$(echo $Fsched | awk -F " " '{print $8 " " $9}')
	LastECCal=$(echo $Fsched | awk -F " " '{print $10 " " $11}')
	CalType=$(echo $Fsched | awk -F " " '{print $12 }')
	Vol=$(echo $Fsched | awk -F " " '{print $13 }')
	Level=$(echo "select Level from farmdata ORDER BY date DESC LIMIT 1;" | mysql -upi -pa-51d41e Farm -N)
	FloodTime='5'
	if [[ $Now > $NextFlood ]] 
	then
                ############################
                #                          #
                # 3way valve at bed pos.   #
                #                          #
                ############################
		gpio -g write 17 1
		gpio -g write 27 0 && sleep 10
		gpio -g write 17 0
		in4=$(date +%T -d "+"$FloodTime"minutes")
		LastFlood=$(date +"%F %T")
		count=0
		while [ $count -lt 3 ]
                do
                        gpio -g write 15 1
                        hall=$(/var/www/hall.py)
                        count=$((count + hall ))
			if (( $(echo "$Level < 100" | bc -l) ))
                        then
	                        Level=$(echo "scale=3;"$Level "+ 1.51" | bc )
				Curve=$(echo "scale=3; "$Level"^2" | bc)
	                fi
#			Aerate
			ShellScreen $Mode
	        done
		nilcount=0
		LastFlood=$(date "+%F %T")
		NextFlood=$(date "+%F %T" --date='+'$period' minutes')
		gpio -g write 17 1
                gpio -g write 27 1
                gpio -g write 17 0
                while [ $nilcount -lt 4 ]                 
		do
			gpio -g write 15 0
                        hall=$(/var/www/hall.py)
                        if [ $hall -eq "0" ]
                        then
                                nilcount=$((nilcount + 1))
                        else
                                nilcount=0
	                        if (( $(echo "$Level > 0" | bc -l) ))
        	                then 
                	                Level=$(echo "scale=3;" $Level" - 1.47" | bc )
					Curve=$(echo "scale=3; -(("$Level" - 5) / 0.5)^2 + 100" | bc)
                        	else
                                	Level="0"
				fi
                        fi
#			Aerate
                        ShellScreen $Mode
                done
                LastpHCal=$(echo $Fsched | awk -F " " '{print $8 " " $9}')
                CalType="Flood"

		Vol="0"
		line=$(echo "'"$(date +"%F %T")"','"$LastFlood"','"$NextFlood"','"$period"','"$LastpHCal"','"$LastECCal"','"$CalType"','"$Vol"'")
                echo "INSERT INTO farmSched (date,LastFlood,NextFlood,period,LastpHCal,LastECCal,CalType,Vol) VALUES ("$line ");"   | mysql -upi -pa-51d41e Farm -N
                #line=$(echo "'"$(date +"%F %T")"','"$LastFlood"','"$NextFlood"','"$period"','"$LastpHCal"','"$CalType"','"$Vol"'")
		#echo "INSERT INTO farmSched (date,LastFlood,NextFlood,period,LastpHCal,CalType,Vol) VALUES ("$line ");" | mysql -upi -pa-51d41e Farm -N

	fi
	Level="0"
	ShellScreen $Mode 
	}


Aerate()
        {
        ####################################
        #                                  #
        #   air pump on/off even minutes   #
        #                                  #
        ####################################
        min=$(date +%M)
#        if [ $((10#${min}%2)) -eq 0 ]
	if [[ $min < 15 ]] 
	then
                gpio -g write 14 1
		if [ $( gpio -g read 27) -eq "0" ]
		then
	                gpio -g write 17 1 
        	        gpio -g write 27 1 
                	gpio -g write 17 0
                	sleep 2
                fi
		gpio -g write 15 1	
	elif [[ $min > 30 ]] && [[ $min < 45 ]]
	then
                gpio -g write 14 1
                if [ $( gpio -g read 27) -eq "0" ]
                then
	                gpio -g write 17 1 
	                gpio -g write 27 1 
	                gpio -g write 17 0
	                sleep 2
		fi
                gpio -g write 15 1
	else
                gpio -g write 14 0
		gpio -g write 15 0
	fi

        #########################
        #                       #
        # rurn the exhaust fan  #
        #   3 min every hour    #
        #########################
	RTemp=$(echo "scale=3;$(cat /sys/bus/w1/devices/28-0000068f125a/w1_slave | awk -F 't=' '{ print $2}') / 1000" | bc)
        ExFanStat=$(gpio -g read 8)
        if [[ $RTemp > 28.5 ]]
        then
                gpio -g write 8 1

        elif [[ $ExFanStat = 1 ]] && [[ $RTemp < 27.5 ]]
        then
                gpio -g write 8 0
        fi

}



Calibrate()
	{
	Mode=$1

	H2O=$(echo "select * from H2O ORDER BY date DESC LIMIT 1;" | mysql -upi -pa-51d41e Farm -N)
	Temp=$(echo $H2O | awk -F" " '{print $3}')
	pH=$(echo $H2O | awk -F" " '{print $4}')
	DeltapH=$(echo $H2O | awk -F" " '{print $5}')
	EV=$(echo $H2O | awk -F" " '{print $6}')
	DeltaEV=$(echo $H2O | awk -F" " '{print $7}')
	TDS=$(echo $H2O | awk -F" " '{print $8}')
	Salt=$(echo $H2O | awk -F" " '{print $9}')
	SG=$(echo $H2O | awk -F" " '{print $10}')

        Fsched=$(echo "select * from farmSched order by date desc limit 1;" | mysql -upi -pa-51d41e Farm -N)
        LastFlood=$(echo $Fsched | awk -F " " '{print $3 " " $4}')
        NextFlood=$(echo $Fsched | awk -F " " '{print $5 " " $6}')
        LastpHCal=$(echo $Fsched | awk -F " " '{print $8 " " $9}')
	LastECCal=$(echo $Fsched | awk -F " " '{print $10 " " $11}')
	CalType=""
        Vol=$(echo $Fsched | awk -F " " '{print $13 }')

	if (( $(echo "$DeltapH < -0.1" | bc -l) ))
	then 
		now=$(date +"%F %T")
                pHDT=$(echo "(" ${now//[-: ]/} " - " ${LastpHCal//[-: ]/} ") / 60" | bc)

		
		############################
		#                          #
		# 3way valve at cycle pos. #
		#                          #
		############################

                Vol=$(echo $DeltapH " * -15" | bc)
                CalType="pH+"
                if (( $(echo "$pHDT > 14" | bc -l) ))
                then
			gpio -g write 17 1 
                	gpio -g write 27 1 && sleep 10
                	gpio -g write 17 0
			gpio -g write 15 1
			LastpHCal=$now
	                line=$(echo "'"$(date +"%F %T")"','"$LastFlood"','"$NextFlood"','"$period"','"$LastpHCal"','"$LastECCal"','"$CalType"','"$Vol"'")
       		        echo "INSERT INTO farmSched (date,LastFlood,NextFlood,period,LastpHCal,LastECCal,CalType,Vol) VALUES ("$line ");"   | mysql -upi -pa-51d41e Farm -N
                fi
	
	elif (( $(echo "$DeltapH > 0.1" | bc -l) ))
	then
		now=$(date +"%F %T")
		pHDT=$(echo "(" ${now//[-: ]/} " - " ${LastpHCal//[-: ]/} ") / 60" | bc)
		Vol=$(echo $DeltapH " * 150" | bc)
		CalType="pH-"
		if (( $(echo "$pHDT > 14" | bc -l) ))
		then
                        gpio -g write 17 1 
                        gpio -g write 27 1 && sleep 10
                        gpio -g write 17 0
                        gpio -g write 15 1
			LastpHCal=$now
                        line=$(echo "'"$(date +"%F %T")"','"$LastFlood"','"$NextFlood"','"$period"','"$LastpHCal"','"$LastECCal"','"$CalType"','"$Vol"'")
                        echo "INSERT INTO farmSched (date,LastFlood,NextFlood,period,LastpHCal,LastECCal,CalType,Vol) VALUES ("$line ");"   | mysql -upi -pa-51d41e Farm -N
		fi
	fi
	if (( $(echo "$DeltaEV < -0.1" | bc -l) )) 
	then
		now=$(date +"%T")
                ECDT=$(echo "(" ${now//[-: ]/} " - " ${LastECCal//[-: ]/} ") / 60" | bc)
                Vol=$(echo $DeltaEV " * -15" | bc)
                CalType=$(echo $Mode "a/b")
                if (( $(echo "$ECDT > 15" | bc -l) ))
                then
                        gpio -g write 17 1 
                        gpio -g write 27 1 && sleep 10
                        gpio -g write 17 0
                        gpio -g write 15 1
                        LastECCal=$now
                        line=$(echo "'"$(date +"%F %T")"','"$LastFlood"','"$NextFlood"','"$period"','"$LastpHCal"','"$LastECCal"','"$CalType"','"$Vol"'")
                        echo "INSERT INTO farmSched (date,LastFlood,NextFlood,period,LastpHCal,LastECCal,CalType,Vol) VALUES ("$line ");"   | mysql -upi -pa-51d41e Farm -N
                fi


	elif (( $(echo "$DeltaEV > 0.1" | bc -l) ))
	then 

		now=$(date +"%F %T")
		ECDT=$(echo "(" ${now//[-: ]/} " - " ${LastECCal//[-: ]/} ") / 60" | bc)
		Vol=$(echo "scale=3;1 / "$DeltaEV  | bc)
		CalType="H2O"
		if (( $(echo "$ECDT > 15" | bc -l) ))
               	then
			LastECCal=$(date +"%F %T")
					####################
					#                  #
					#  open water tap  #
					#		   #
					####################
               		line=$(echo "'"$(date +"%F %T")"','"$LastFlood"','"$NextFlood"','"$period"','"$LastpHCal"','"$LastECCal"','"$CalType"','"$Vol"'")
               		echo "INSERT INTO farmSched (date,LastFlood,NextFlood,period,LastpHCal,LastECCal,CalType,Vol) VALUES ("$line ");"   | mysql -upi -pa-51d41e Farm -N
		fi
	else
		if [ $(gpio -g read 14) -eq 0 ]
                then
			gpio -g write 15 0
		fi
	fi
	}

        ##########################
        #                        #
        #  shell status display  #
        #                        #
        ##########################
ShellScreen()
        {
	Mode=$1
        if [[ $Mode="Flowering" ]]
        then
                TargetEC="2.400"
        elif [[ $Mode="Vegetative" ]]
        then
                TargetEC="1.800"
        fi
	H2O=$(echo "select * from H2O ORDER BY date DESC LIMIT 1;" | mysql -upi -pa-51d41e Farm -N)
        pH=$(echo "select pH from H2O ORDER BY date DESC LIMIT 1;" | mysql -upi -pa-51d41e Farm -N)
        EC=$(echo "select EV from H2O ORDER BY date DESC LIMIT 1;" | mysql -upi -pa-51d41e Farm -N)     
        TDS=$(echo "select TDS from H2O ORDER BY date DESC LIMIT 1;" | mysql -upi -pa-51d41e Farm -N)
        Salt=$(echo "select Salt from H2O ORDER BY date DESC LIMIT 1;" | mysql -upi -pa-51d41e Farm -N)
	SG=$(echo "select SG from H2O ORDER BY date DESC LIMIT 1;" | mysql -upi -pa-51d41e Farm -N)
	farmdata=$(echo "select * from farmdata ORDER BY date DESC LIMIT 1;" | mysql -upi -pa-51d41e Farm -N)
	DayInMode=$(echo "select DayInMode from farmdata ORDER BY date DESC LIMIT 1;" | mysql -upi -pa-51d41e Farm -N)
	LTemp=$(echo "select LampTemp from farmdata ORDER BY date DESC LIMIT 1;" | mysql -upi -pa-51d41e Farm -N)
        RTemp=$(echo "select RoomTemp from farmdata ORDER BY date DESC LIMIT 1;" | mysql -upi -pa-51d41e Farm -N)
        TTemp=$(echo "select Temp from H2O ORDER BY date DESC LIMIT 1;" | mysql -upi -pa-51d41e Farm -N)
        AirStatus=$(gpio -g read 14)
        PumpStatus=$(gpio -g read 15)
	ValveStatus=$(gpio -g read 27)
        LigthStatus=$(gpio -g read 18)
        Drain=$(/var/www/hall.py )
        ExhaustFan=$(gpio -g read 8)
        if [ $AirStatus -eq "0" ]
        then
                AirStatusTxt="Off"
        elif [ $AirStatus -eq "1"  ]
        then
                AirStatusTxt="On  "
        fi

        if [ $PumpStatus -eq "0" ]
        then
		PumpTxtEx="Off\t "
                PumpStatusTxt="Off"
        elif [ $PumpStatus -eq "1"  ]
        then
		if [ $ValveStatus  -eq "0" ]
                then 
			PumpStatusTxt="On"
			PumpTxtEx="Bed\t "
		
		elif [ $ValveStatus  -eq "1" ]
		then
			PumpStatusTxt="On"
			PumpTxtEx="Recycle "
		fi
        fi

        if [ $LigthStatus -eq "0" ]
        then
                LigthStatusTxt="Off"
        elif [ $LigthStatus -eq "1"  ]
        then
           	LigthStatusTxt="On "
        fi
        if [ $Drain -eq "0" ]
        then
                Drain="Off"
        else
                Drain="On "
        fi
       if [ $ExhaustFan -eq "0" ]
        then
                ExFan="Off"
       else
                ExFan="On "
        fi
        #Level=$(echo "SELECT Level FROM farmdata ORDER BY date DESC LIMIT 1;" | mysql -upi -pa-51d41e Farm -N )
        Curve=$(echo "scale=3; ("$Level"^2) / 55" | bc)
        line=$(echo "'"$(date +%F-%H:%M:%S)"','"$LigthStatusTxt"','"$ExFan"','"$AirStatusTxt"','"$PumpStatusTxt"','"$Drain"','"$Level"','"$Mode"','"$DayInMode"','"$LTemp"','"$RTemp"'")
        echo "INSERT INTO farmdata (date,lights,ExFan,AirPump,WaterPump,Drain,Level,mode,DayInMode,LampTemp,RoomTemp) VALUES ("$line ");" | mysql -upi -pa-51d41e Farm -N
        echo "COMMIT;" | mysql -upi -pa-51d41e Farm -N
        echo -e ' \t ' > ./ScreenFile
        echo  -e "GrowBot6" >> ./ScreenFile
        date +"%D %T" >> ./ScreenFile
        echo  -e "An Evil Scientist SINdicate production" >> ./ScreenFile
        echo  -e "" >> ./ScreenFile
        echo  -e "Mode:" $Mode "\t LightOn:"$LightOn":00    LightOff: "$LightOff":00" >> ./ScreenFile
        echo  -e "Light Status       :\t" $LigthStatusTxt >> ./ScreenFile
        echo  -e "Exhaust Fan status :\t" $ExFan >> ./ScreenFile
        echo  -e "AirPump Status     :\t" $AirStatusTxt >> ./ScreenFile
        echo  -e "Pump Status        :\t" $PumpTxtEx"Period: "$period" Min" >> ./ScreenFile
        echo  -e "Drain              :\t" $Drain "\t Last flood: " $LastFlood >> ./ScreenFile
        echo  -e "\t\t\t\t Next flood: " $NextFlood >> ./ScreenFile
        echo  -e "\t\t\t\t level: " $Level "\tCurve:" $Curve>> ./ScreenFile
        echo  -e "" >> ./ScreenFile
        echo  -e "pH              : " $pH "\t Delta" $(echo "scale=3; "$pH "- 5.8" | bc | sed -r 's/^(-?)\./\10./') "[5.6/5.8/6.0]" >> ./ScreenFile
        echo  -e "Conductivity    : " $EC "\t Delta" $(echo "scale=3; "$EC "-" $TargetEC  | bc | sed -r 's/^(-?)\./\10./') "["$Mode": "$TargetEC"]" >> ./ScreenFile
        echo  -e "TDS             : " $TDS >> ./ScreenFile
        echo  -e "Salinity        : " $Salt >> ./ScreenFile
        echo  -e "Specific Gravity: " $SG >> ./ScreenFile
        echo  -e "" >> ./ScreenFile
        echo  -e "Temp Lamp       : " $LTemp >> ./ScreenFile
        echo  -e "Temp Mid Room   : " $RTemp >> ./ScreenFile
        echo  -e "Temp Tank       : " $TTemp >> ./ScreenFile
        echo  -e "" >> ./ScreenFile
        echo  -e "select date, mode, DayInMode, lights, ExFan, AirPump, WaterPump, Drain, Level, LampTemp, RoomTemp from farmdata ORDER BY date DESC LIMIT 5 " | mysql -upi -pa-51d41e -t Farm >> ./ScreenFile
        echo  -e "select * from farmSched ORDER BY date DESC LIMIT 5 " | mysql -upi -pa-51d41e -t Farm > ./Screen2File
        echo  -e "select * from H2O order by date desc limit 5;" | mysql -t -upi -pa-51d41e Farm >> ./Screen2File
        sed -e 's/^/                              /' ./Screen2File >> ./ScreenFile && rm -f ./Screen2File
        clear
        cat ./ScreenFile
	}












while true 
do
	if [[ -z $(sudo ps -A | grep "readsensor.sh") ]]
        then
                /usr/bin/screen  -dm -S ReadSensors ~/readsensor.sh $Mode 
        fi
	if [[ -z $(service grafana-server status | grep -c "Active: active") ]]
	then
		service grafana-server start
	fi
	Lights $LightOn $LightOff $period
	Water $Mode $period
	Aerate
	Calibrate $Mode
done
