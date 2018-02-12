
pH=$(./pH.py)
while [ -z $pH ]
do
	pH=$(./pH.py)
	sleep 2
done

if  [ $(echo "scale=3;"$pH "< 5.6" | bc ) -eq 1 ]
then
	echo $pH "pH low"
	AvgpH=0
	for i in $(echo "select ph from farmdata order by date desc  limit 10;" | mysql -N  -uroot -pa-51d41e Farm)
	do
		AvgpH=$( echo "scale=3;" $AvgpH " + " $i | bc)
	done
	AvgpH=$(echo "scale=3;" $AvgpH "/10" | bc)
	echo $AvgpH
#	if  [ $(echo "scale=3;"$AvgpH "< 5.5" | bc ) -eq 1 ]
#	then
#		echo "Avg pH low"
#		echo "rectify pH"
#	elif  [ $(echo "scale=3;"$AvgpH "> 5.9" | bc ) -eq 1 ]
#       then
#                echo "Avg pH high"
#       fi
#	else    echo $AvgpH "is within
elif  [ $(echo "scale=3;"$pH "> 6.0" | bc ) -eq 1 ]
then
	echo $pH "pH high"
	AvgpH=0
        for i in $(echo "select ph from farmdata order by date desc limit 10;" | mysql -N  -uroot -pa-51d41e Farm)
        do
                AvgpH=$( echo "scale=3;" $AvgpH " + " $i | bc)
#		echo $i $AvgpH
        done
        AvgpH=$(echo "scale=3;" $AvgpH "/10" | bc)
#	echo  $AvgpH
	if  [ $(echo "scale=3;"$AvgpH "< 5.5" | bc ) -eq 1 ]
        then
                echo $AvgpH "Avg low"
		echo 'select date pH from farmdata order by date desc limit 10;' | mysql -t -upi -pa-51d41e Farm
        elif  [ $(echo "scale=3;"$AvgpH "> 5.9" | bc ) -eq 1 ]
        then
                echo $AvgpH "Avg high"
		echo 'select date pH from farmdata order by date desc limit 10;' | mysql -t -upi -pa-51d41e Farm
		echo "recify pH"
		echo "Air pump: On"
		LastpHCal=$(date +%T)
		NextpHCal=$(date  "+%T" -d " 30 minutes")
		gpio -g write 14 1
		gpio -g write 17 0	#(valves tank cycle dont go to beds	
		gpio -g write 15 1      #
		
		./Squiddy.py -s phm -v 25
       else
		echo $AvgpH "is within tolerance"
	fi
else
	echo "oki " $pH "is within tolerance"
fi 
while true
do
	gpio -g write 14 1
        gpio -g write 17 0      #(valves tank cycle dont go to beds
        gpio -g write 15 1
	clear
	AvgpH=0
	for i in $(echo "select ph from farmdata order by date desc  limit 10;" | mysql -N  -uroot -pa-51d41e Farm)
        do
                AvgpH=$( echo "scale=3;" $AvgpH " + " $i | bc)
        done
        AvgpH=$(echo "scale=3;" $AvgpH "/10" | bc)
	date +%T
        echo "pH: " $(./pH.py) "Average pH: "$AvgpH
	echo 'select date, pH from farmdata order by date desc limit 10;' | mysql -t -upi -pa-51d41e Farm
	echo "Next calibration :" $NextpHCal
	sleep 7
done
gpio -g write 14 0
gpio -g write 15 0
