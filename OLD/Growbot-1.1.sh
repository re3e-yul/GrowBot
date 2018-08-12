#! /bin/bash

########
#      #
# init #
#      #
########

if [[ $# -eq 0 ]] ; then
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
                LightOn="07"
                LightOff="19"
                ;;
                Vegetative)
                LightOn="06"
                LightOff="22"
                ;;
esac
done
Level="0"
date=$(date +%T)
LastFlood=$(echo "SELECT LastFlood FROM farmSched ORDER BY date DESC LIMIT 1;" | mysql -upi -pa-51d41e Farm -N)
NextFlood=$(echo "SELECT NextFlood FROM farmSched ORDER BY date DESC LIMIT 1;" | mysql -upi -pa-51d41e Farm -N)
if [[ $NextFlood = "0000-00-00 00:00:00" ]] 
then
        LastFlood=$(date  "+%T")
        NextFlood=$(date  "+%T")
fi

gpio -g mode 14 out
gpio -g mode 15 out
gpio -g mode 18 out
gpio -g mode 17 out
gpio -g mode 27 out
AirStatus=$(gpio -g read 14)
ExhaustStatus=$(gpio -g read 8)
PumpStatus=$(gpio -g read 15)
LigthStatus=$(gpio -g read 18)


########
#      #
# Libs #
#      #
########


        ##########################
        #                        #
        #  shell status display  #
        #                        #
        ##########################
        ShellScreen()
        {
        if [ -z $pH ] && [ -z $EV ]
        then
                pH=$(echo "select pH from H2O ORDER BY date DESC LIMIT 1;" | mysql -upi -pa-51d41e Farm -N)
                EC=$(echo "select EV from H2O ORDER BY date DESC LIMIT 1;" | mysql -upi -pa-51d41e Farm -N)     
                TDS=$(echo "select TDS from H2O ORDER BY date DESC LIMIT 1;" | mysql -upi -pa-51d41e Farm -N)
                Salt=$(echo "select Salt from H2O ORDER BY date DESC LIMIT 1;" | mysql -upi -pa-51d41e Farm -N)
                SG=$(echo "select SG from H2O ORDER BY date DESC LIMIT 1;" | mysql -upi -pa-51d41e Farm -N)
                Tsens1=$(echo "select Temp from H2O ORDER BY date DESC LIMIT 1;" | mysql -upi -pa-51d41e Farm -N)
                Tsens2=$(echo "select LampTemp from farmdata ORDER BY date DESC LIMIT 1;" | mysql -upi -pa-51d41e Farm -N)
                Tsens3=$(echo "select SoilTemp from farmdata ORDER BY date DESC LIMIT 1;" | mysql -upi -pa-51d41e Farm -N)
                Level=$(echo "select Level from farmdata ORDER BY date DESC LIMIT 1;" | mysql -upi -pa-51d41e Farm -N)
        fi
        AirStatus=$(gpio -g read 14)
        PumpStatus=$(gpio -g read 15)
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
                PumpStatusTxt="Off"
        elif [ $PumpStatus -eq "1"  ]
        then
                PumpStatusTxt="On  "
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
        line=$(echo "'"$(date +%F-%H:%M:%S)"','"$LigthStatusTxt"','"$ExFan"','"$AirStatusTxt"','"$PumpStatusTxt"','"$Drain"','"$Level"','"$Mode"','"$Tsens2"','"$Tsens1"'")
        echo "INSERT INTO farmdata (date,lights,ExFan,AirPump,WaterPump,Drain,Level,mode,LampTemp,SoilTemp) VALUES ("$line ");" | mysql -upi -pa-51d41e Farm -N
        echo "COMMIT;" | mysql -upi -pa-51d41e Farm -N
        Level=$(echo "SELECT Level FROM farmdata ORDER BY date DESC LIMIT 1;" | mysql -upi -pa-51d41e Farm -N )
        echo -e ' \t ' > ./ScreenFile
        echo  -e "GrowBot6" >> ./ScreenFile
        date +%T >> ./ScreenFile
        echo  -e "An Evil Scientist SINdicate production" >> ./ScreenFile
        echo  -e "" >> ./ScreenFile
        echo  -e "Mode:" $Mode "\t LightOn:"$LightOn":00    LightOff: "$LightOff":00" >> ./ScreenFile
        echo  -e "Light Status       :\t" $LigthStatusTxt >> ./ScreenFile
        echo  -e "Exhaust Fan status :\t" $ExFan >> ./ScreenFile
        echo  -e "AirPump Status     :\t" $AirStatusTxt >> ./ScreenFile
        echo  -e "Pump Status        :\t" $PumpStatusTxt "\t Period: " $period"Min" $(gpio -g read 17)/$(gpio -g read 27) "En/Bed" >> ./ScreenFile
        echo  -e "Drain              :\t" $Drain "\t Last flood: " $LastFlood >> ./ScreenFile
        echo  -e "\t\t\t\t Next flood: " $NextFlood >> ./ScreenFile
#       echo  -e "\t\t\t\t High level: " $BedHighLevelTxt >> ./ScreenFile
#        echo  -e "\t\t\t\t Mid  level: " $BedMidLevelTxt >> ./ScreenFile
#        echo  -e "\t\t\t\t Low  level: " $BedLowLevelTxt >> ./ScreenFile
        echo  -e "\t\t\t\t level: " $Level >> ./ScreenFile
        echo  -e "" >> ./ScreenFile
        echo  -e "pH              : " $pH "\t Delta" $(echo "scale=3; "$pH "- 5.8" | bc | sed -r 's/^(-?)\./\10./') "[5.6/5.8/6.0]" >> ./ScreenFile
        echo  -e "Conductivity    : " $EC >> ./ScreenFile
        echo  -e "TDS             : " $TDS >> ./ScreenFile
        echo  -e "Salinity        : " $Salt >> ./ScreenFile
        echo  -e "Specific Gravity: " $SG >> ./ScreenFile
        echo  -e "" >> ./ScreenFile
        echo  -e "Temp Lamp       : " $Tsens1 >> ./ScreenFile
        echo  -e "Temp Mid Room   : " $Tsens2 >> ./ScreenFile
        echo  -e "Temp Tank       : " $Tsens3 >> ./ScreenFile
        echo  -e "" >> ./ScreenFile
        echo  -e "select date, mode, lights, ExFan, AirPump, WaterPump, Drain, Level, LampTemp, SoilTemp from farmdata ORDER BY date DESC LIMIT 7 " | mysql -upi -pa-51d41e -t Farm >> ./ScreenFile
        echo  -e "select * from farmSched ORDER BY date DESC LIMIT 7 " | mysql -upi -pa-51d41e -t Farm > ./Screen2File
        echo  -e "select * from H2O order by date desc limit 7;" | mysql -t -upi -pa-51d41e Farm >> ./Screen2File
#       "\t\t\t"
        sed -e 's/^/                              /' ./Screen2File >> ./ScreenFile && rm -f ./Screen2File
        clear
        cat ./ScreenFile
        }







Lights()
        {
        #######################
        #                     #
        #  Turn on the lights #
        #                     #
        #######################
        LightOn=$1
        LightOff=$2
        if [ $(/bin/date +%H) -ge $LightOn ] && [ $(/bin/date +%H) -lt $LightOff ]
        then
                #echo "day"
                if [ $(gpio -g read 18) -eq 0 ]
                then
                        gpio -g write 18 1
                fi
        else
                #echo "night"
                if [ $(gpio -g read 18) -eq 1 ]
                then
                        gpio -g write 18 0
                fi
        fi
        
}

water()
	{
	now=$(date +"%F %T")
	LastFlood=$(echo "SELECT LastFlood FROM farmSched ORDER BY date DESC LIMIT 1;" | mysql -upi -pa-51d41e Farm -N)
	NextFlood=$(echo "SELECT NextFlood FROM farmSched ORDER BY date DESC LIMIT 1;" | mysql -upi -pa-51d41e Farm -N)
        if [[ $now > $NextFlood ]] || [[ $ForceFlood -eq "1" ]] || [[ $NextFlood = "00:00:00" ]]
        then
		in3=$(date +%T -d "+4minutes")
		while [[ $now < $in3 ]]
		do
			do
                        if [ $(gpio -g read 15) -eq 0 ]
                        then
                                gpio -g write 15 1
                        fi
                        now=$(date +"%D %T")
                        hall=$(/var/www/hall.py)
                        Level=$(echo $Level + 8.7 | bc )
                        ReadSensor
                        Lights $LightOn $LightOff
                        Aerate
                        ShellScreen $Mode $period $LastFlood $NextFlood
                done
                
#                while [[ $(/var/www/hall.py) -eq 1 ]]
		while [[ $Level -gt 0 ]]
                do
                        if [ $(gpio -g read 15) -eq 1 ]
                        then
                                gpio -g write 15 0
                        fi
                        now=$(date +"%D %T")
                        hall=$(/var/www/hall.py)
                        Level=$(echo $Level - 8.7 | bc )
                        ReadSensor
                        Lights $LightOn $LightOff
                        Aerate
                        ShellScreen $Mode $period $LastFlood $NextFlood
                done
                Level="0"

	done
	gpio -g write 15 0
	
done
}





########
#      #
# main #
#      #
########

while true
do
	Lights $LightOn $LightOff
	Water $period
	ShellScreen $Mode $period
done
