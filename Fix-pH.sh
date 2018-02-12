#!/bin/bash
pH=$(./pH.py)
Delta=$( echo 'scale=2; (5.8 -' $pH ') * 10' | bc)
while [ $pH > '5.8' ]
do
	pH=$(./pH.py)
	DeltaPh=$( echo 'scale=2; (5.8 -' $pH ') ' | bc)
	if [ Delta < '0' ]
	then 
		echo "pH: "$pH" Delta: "$DeltaPh
		vol=$(echo '25 * (-' $DeltaPh')/1' | bc)
		echo "vol: "$vol "mL"
		./Squiddy.py -s phm -v $vol
	elif [ Delta > '0' ]
        then
		echo "pH: "$pH" Delta: "$Delta
                #./Squiddy.py -s php -v $Dela
	fi
	MinNow=$(date +%M)
	MinStop=$(echo 'scale=1; 7 + ' $MinNow | bc)
	Delta=$(echo 'scale=2;(' $MinStop ' - ' $(date +%M)') * 60'  | bc)
	date
	while [ $(date +%M) -lt $MinStop ]
	do
		Delta=$(echo 'scale=2;(' $MinStop ' - ' $(date +%M)') * 60 + (60 - ' $(date +%S) ')'  | bc)
		pH=$(./pH.py)
	        DeltaPh=$( echo 'scale=2; (5.8 -' $pH ')' | bc)
		echo "Ph: "$pH "Delta Ph: "$DeltaPh "recalibrating in " $Delta "seconds" 
        	gpio -g write 14 1
        	#./pH.py 
        	sleep 4
done
gpio -g write 14 0
echo "Done"
	
done
echo pH=$(./pH.py)
echo "pH stabilized"
