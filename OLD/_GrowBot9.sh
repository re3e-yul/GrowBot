! /bin/bash
if [[ $# -eq 0 ]] ; then
    echo "Usage: GrowBot6.sh -fF/-gG [Hour period]"
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
#echo "Mode: " $Mode "Period:" $period && sleep 4
date=$(date +%T)
LastFlood=$(echo "SELECT LastFlood FROM farmSched ORDER BY date DESC LIMIT 1;" | mysql -upi -pa-51d41e Farm -N)
NextFlood=$(echo "SELECT NextFlood FROM farmSched ORDER BY date DESC LIMIT 1;" | mysql -upi -pa-51d41e Farm -N)
if [[ $NextFlood = "00:00:00" ]] 
then
	LastFlood=$(date  "+%T")
	NextFlood=$(date  "+%T")
fi
#if [[ $NextFlood -gt $(date  "+%T" -d $period" hours") ]]
#then
#	echo "It's been a long time baby ...."
#	NextFlood
#fi
gpio -g mode 14 out
gpio -g mode 15 out
gpio -g mode 18 out
gpio -g mode 17 out
gpio -g mode 27 out
gpio -g mode 23 in
gpio -g mode 24 in
gpio -g mode 25 in
AirStatus=$(gpio -g read 14)
PumpStatus=$(gpio -g read 15)
LigthStatus=$(gpio -g read 18)

	
###########################################################
###########################################################
	##########################
        #                        #
        #  shell status display  #
        #                        #
        ##########################
        ShellScreen()
        {
        AirStatus=$(gpio -g read 14)
        PumpStatus=$(gpio -g read 15)
        LigthStatus=$(gpio -g read 18)
	BedHighLevel=$(gpio -g read 23)
        BedMidLevel=$(gpio -g read 24)
        BedLowLevel=$(gpio -g read 25)
        Drain=$(/var/www/hall.py | wc -l)
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

	if [ $BedHighLevel -eq "0" ]
        then
                BedHighLevelTxt="Low"
        elif [ $BedHighLevel -eq "1"  ]
        then
                BedHighLevelTxt="High"
        fi
        
        if [ $BedMidLevel -eq "0" ]
        then
                BedMidLevelTxt="Low"
        elif [ $BedMidLevel -eq "1"  ]
        then
                BedMidLevelTxt="High"
        fi
        
	if [ $BedLowLevel -eq "1" ]
        then
                BedLowLevelTxt="Low"
        elif [ $BedLowLevel -eq "0"  ]
        then 
                BedLowLevelTxt="High"
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
	
	line=$(echo "'"$(date +%F-%H:%M:%S)"','"$LigthStatusTxt"','"$ExFan"','"$AirStatusTxt"','"$PumpStatusTxt"','"$Drain"','"$BedHighLevelTxt"','"$BedMidLevelTxt"','"$BedLowLevelTxt"','"$Level"','"$Mode"','"$pH"','"$Tsens2"','"$Tsens1"'")
        echo "INSERT INTO farmdata (date,lights,ExFan,AirPump,WaterPump,Drain,HighLevel,MidLevel,LowLevel,Level,mode,pH,LampTemp,SoilTemp) VALUES ("$line ");" | mysql -upi -pa-51d41e Farm -N
#        line2=$(echo "'"$(date +%F-%H:%M:%S)"','"$LastFlood"','"$NextFlood"','"$period"','"$LastpHCal"','"$NextpHCal"','"$Vol"'")
#        echo "INSERT INTO farmSched (date,LastFlood,NextFlood,period,LastpHCal,NextpHCal,Vol) VALUES ("$line2 ");" | mysql -upi -pa-51d41e Farm -N
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
	echo  -e "Pump Status        :\t" $PumpStatusTxt "\t Period: " $period"h" $(gpio -g read 17)/$(gpio -g read 27) "En/Bed" >> ./ScreenFile
	echo  -e "Drain              :\t" $Drain "\t Last flood: " $LastFlood >> ./ScreenFile
	echo  -e "\t\t\t\t Next flood: " $NextFlood >> ./ScreenFile
	echo  -e "\t\t\t\t High level: " $BedHighLevelTxt >> ./ScreenFile
        echo  -e "\t\t\t\t Mid  level: " $BedMidLevelTxt >> ./ScreenFile
        echo  -e "\t\t\t\t Low  level: " $BedLowLevelTxt >> ./ScreenFile
	echo  -e "\t\t\t\t level: " $Level >> ./ScreenFile
        echo  -e "" >> ./ScreenFile
        echo  -e "pH              : " $pH "\t Delta" $(echo "scale=3; "$pH "- 5.8" | bc | sed -r 's/^(-?)\./\10./') "[5.6/5.8/6.0]" >> ./ScreenFile
        echo  -e "Conductivity    : " $EC >> ./ScreenFile
        echo  -e "TDS             : " $TDS >> ./ScreenFile
        echo  -e "Salinity        : " $Salt >> ./ScreenFile
        echo  -e "Specific Gravity: " $SG >> ./ScreenFile
	echo  -e "Temp Lamp       : " $Tsens2 >> ./ScreenFile
        echo  -e "Temp Mid Room   : " $Tsens1 >> ./ScreenFile
        echo  -e "" >> ./ScreenFile
	echo  -e "" >> ./ScreenFile
	echo  -e "" >> ./ScreenFile
	echo  -e "select date, mode, lights, ExFan, AirPump, WaterPump, Drain, HighLevel, MidLevel, LowLevel, Level, pH, LampTemp, SoilTemp from farmdata ORDER BY date DESC LIMIT 10 " | mysql -upi -pa-51d41e -t Farm >> ./ScreenFile
	echo -e ""  >> ./ScreenFile
	echo  -e "\t\t\t""select * from farmSched ORDER BY date DESC LIMIT 10 " | mysql -upi -pa-51d41e -t Farm > ./Screen2File
	sed -e 's/^/                              /' ./Screen2File >> ./ScreenFile && rm -f ./Screen2File
	clear
	cat ./ScreenFile
	}
################################################################################

###############################################################################
###############################################################################
ReadSensor()
	{
	pH=$(/var/www/pH.py)
	ECs=$(/var/www/EC.py)
	EC=$(echo $ECs | awk -F " " '{print $1 }')
	TDS=$(echo $ECs | awk -F " " '{print $2 }')
	Salt=$(echo $ECs | awk -F " " '{print $3 }')
	SG=$(echo $ECs | awk -F " " '{print $4 }')
#        Tsens1=$(echo "scale=3;$(for Tsens in $(ls -d /sys/bus/w1/devices/28-*); do cat $Tsens/w1_slave | tail -n 1 | awk -F"=" '{ print $2}'; done | head -n 1)/1000" |bc )
#        Tsens2=$(echo "scale=3;$(for Tsens in $(ls -d /sys/bus/w1/devices/28-*); do cat $Tsens/w1_slave | tail -n 1 | awk -F"=" '{ print $2}'; done | tail -n 1)/1000" |bc)
        }
################################################################################


################################################################################
################################################################################

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
		gpio -g write 18 1
        else
		#echo "night"
                gpio -g write 18 0
        fi
	
}
################################################################################


################################################################################
###############################################################################
Water()
	{
        #############################
        #                           #
        # water the bed for 2 min   #
        #                           #
        #############################
	
	for bed in {0..0}
	do
		Now=$(date +%T)
		NextFlood=$(echo "SELECT NextFlood FROM farmSched ORDER BY date DESC LIMIT 1;" | mysql -upi -pa-51d41e Farm -N )
		if [[ $Now > $NextFlood ]] || [[ $ForceFlood -eq "1" ]] || [[ $NextFlood = "00:00:00" ]]
		then
			Level=0
			gpio -g write 17 1
			gpio -g write 27 $bed
		hall=$(/var/www/hall.py | wc -l)
 			PumpStatus=$(gpio -g read 15)
			while [[ $(echo "scale=3;"$Level "< 100" | bc ) -eq 1  ]] && [[ $hall -eq "0"  ]]  #no water true drain 
			do
				Level=$(echo $Level + 2.29 | bc )
                        	gpio -g write 15 1 # Water Pump ON
				ReadSensor
#				CorrectpH
				Lights $LightOn $LightOff
				Aerate
				ShellScreen $Mode $period $LastFlood $NextFlood
				hall=$(/var/www/hall.py | wc -l)
                	done
			while [[ $hall -gt "0" ]] # || [[ $(echo "scale=3;"$Level ">0" | bc ) -eq 1 ]]
			do
        			Level=$(echo $Level - 2.29 | bc )
				gpio -g write 15 0
				ReadSensor
#				CorrectpH
				Lights $LightOn $LightOff
                                ShellScreen $Mode $period $LastFlood $NextFlood
                                Aerate
        			hall=$(/var/www/hall.py | wc -l)
			done
			level="0"
			gpio -g write 15 0
			gpio -g write 17 0
			LastFlood=$(date  "+%T")
        		NextFlood=$(date  "+%T" -d $period" hours")
			LastpHCal=$(echo "SELECT LastpHCal FROM farmSched ORDER BY date DESC LIMIT 1;" | mysql -upi -pa-51d41e Farm -N)
			NextpHCal=$(echo "SELECT NextpHCal FROM farmSched ORDER BY date DESC LIMIT 1;" | mysql -upi -pa-51d41e Farm -N)
			Vol=$(echo "SELECT Vol FROM farmSched ORDER BY date DESC LIMIT 1;" | mysql -upi -pa-51d41e Farm -N)
		        line2=$(echo "'"$(date +%F-%H:%M:%S)"','"$LastFlood"','"$NextFlood"','"$period"','"$LastpHCal"','"$NextpHCal"','"$Vol"'")
		        echo "INSERT INTO farmSched (date,LastFlood,NextFlood,period,LastpHCal,NextpHCal,Vol) VALUES ("$line2 ");" | mysql -upi -pa-51d41e Farm -N
	        	ForceFlood="0"
		else
			gpio -g write 15 0
                        gpio -g write 17 0
		fi
		gpio -g write 15 0
                gpio -g write 17 0
	done
	if [ $BedLowLevel -eq "0"  ]
	then
		Level="0"
	fi
	}
################################################################################



################################################################################
###############################################################################
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
	#RoomTemp=$(echo "scale=3;$(for Tsens in $(ls -d /sys/bus/w1/devices/28-*); do cat $Tsens/w1_slave | tail -n 1 | awk -F"=" '{ print $2}'; done | head -n 1)/1000" |bc )
        #if [ $(/bin/date +%M) -ge $AirOut ] || [[ $RoomTemp > 29 ]] 
	if [[ $RoomTemp > 29 ]]
	then
                gpio -g write 8 1

	elif [[ $ExFanStat = 1 ]] && [[ $RoomTemp < 28.5 ]]
        then
	        gpio -g write 8 0
#	else
#		gpio -g write 8 0
        fi

}


##################################################################################
CorrectpH()
	{

Now=$(date +%T)
#if [[ -z $LastpHCal ]] || [[ -z $NextpHCal]]
#then
	LastpHCal=$(echo "SELECT LastpHCal FROM farmSched ORDER BY date DESC LIMIT 1;" | mysql -upi -pa-51d41e Farm -N )
	NextpHCal=$(echo "SELECT NextpHCal FROM farmSched ORDER BY date DESC LIMIT 1;" | mysql -upi -pa-51d41e Farm -N )
#fi

if [[ $Now > $NextpHCal ]]  || [[ $NextpHCal = "00:00:00" ]] && [[ $pH != "0" ]]
then


	pH=$(./pH.py)
	while [ -z $pH ]
	do
        	pH=$(/var/www/pH.py)
	        sleep 2
	done
	 
	##########
	# pH low #
	##########

	if  [ $(echo "scale=3;"$pH "< 5.6" | bc ) -eq 1 ]
	then
	        AvgpH=0
	        for i in $(echo "select ph from farmdata order by date desc  limit 10;" | mysql -N  -uroot -pa-51d41e Farm)
        	do
                	AvgpH=$( echo "scale=3;" $AvgpH " + " $i | bc)
	        done
        	AvgpH=$(echo "scale=3;" $AvgpH "/10" | bc)
	        if  [ $(echo "scale=3;"$AvgpH "< 5.7" | bc ) -eq 1 ]
	        then
			pHDelta=$(echo "scale=3;5.8 - " $pH | bc)
                	echo "pH: "$$pH "Avg low" $AvgpH ",Delta:" $pHDelta 
	                echo 'select date pH from farmdata order by date desc limit 10;' | mysql -t -upi -pa-51d41e Farm
        	        echo "recify pH, Selection pH+"
                	echo "Air pump: On"
	                LastpHCal=$(date  "+%T")
        	        gpio -g write 14 1      #airpump on
                	gpio -g write 17 0      #valves tank cycle dont go to beds
	                gpio -g write 15 1      #waterpump on
			pHDelta=$(echo "scale=3;5.8 - " $pH | bc)
			Vol=$(echo 'scale=3;' $pHDelta ' * 0.5' | bc)
                        echo "Calibrating Delta pH of " $pHDelta "with " $Vol"mL of pH+"
#                       ./Squiddy.py -s php -v 15
	                NextpHCal=$(date  "+%T" -d " 20 minutes")
			line2=$(echo "'"$(date +%F-%H:%M:%S)"','"$LastFlood"','"$NextFlood"','"$period"','"$LastpHCal"','"$NextpHCal"','"$Vol"'")

        	fi

	###########
	# pH high #
	###########
	elif  [ $(echo "scale=3;"$pH "> 6.0" | bc ) -eq 1 ]
	then
                AvgpH=0
        	for i in $(echo "select ph from farmdata order by date desc limit 10;" | mysql -N  -uroot -pa-51d41e Farm)
	        do
	                AvgpH=$( echo "scale=3;" $AvgpH " + " $i | bc)
	        done
        	AvgpH=$(echo "scale=3;" $AvgpH "/10" | bc)
	        ####################
		# Check average pH #
		####################
		if  [ $(echo "scale=3;"$AvgpH "> 5.9" | bc ) -eq 1 ]
	        then
        	        pHDelta=$(echo "scale=3;5.8 - " $pH | bc)
                	LastpHCal=$(date  "+%T")
        	        gpio -g write 14 1	#airpump on
                	gpio -g write 17 0      #valves tank cycle dont go to beds
	                gpio -g write 15 1      #waterpump on 
			pHDelta=$(echo "scale=3;5.8 - " $pH | bc)
			Vol=$(echo 'scale=3;' $pHDelta ' * 0.5' | bc)
                        ./Squiddy.py -s phm -v 15
			NextpHCal=$(date  "+%T" -d "15 minutes")		
        		line2=$(echo "'"$(date +%F-%H:%M:%S)"','"$LastFlood"','"$NextFlood"','"$period"','"$LastpHCal"','"$NextpHCal"','"$Vol"'")
		fi
	else
		Vol="0"
		LastpHCal=$(date  "+%T")
		NextpHCal=$(date  "+%T" -d "15 minutes")
		line2=$(echo "'"$(date +%F-%H:%M:%S)"','"$LastFlood"','"$NextFlood"','"$period"','"$LastpHCal"','"$NextpHCal"','"$Vol"'")

	fi
else
	Vol="0"
	line2=$(echo "'"$(date +%F-%H:%M:%S)"','"$LastFlood"','"$NextFlood"','"$period"','"$LastpHCal"','"$NextpHCal"','"$Vol"'")
fi
echo "INSERT INTO farmSched (date,LastFlood,NextFlood,period,LastpHCal,NextpHCal,Vol) VALUES ("$line2 ");" | mysql -upi -pa-51d41e Farm -N
	}
##################################################################################
##################################################################################

if [[ -z $(sudo ps -A | grep "PlotIt.py") ]]
then
	/usr/bin/screen  -dm -S WebPloter /var/www/PlotIt.py 
fi

while true
do
	ShellScreen $Mode $period $LastFlood $NextFlood
	Lights $LightOn $LightOff
	ReadSensor
	CorrectpH
	Water $period
        Aerate
	if [[ "$Level" > "0" ]] && [[ $(gpio -g read 15) -eq "0" ]]
        then
                Level=$(echo $Level - 1.41 | bc )

        else
                Level=0
        fi
done

