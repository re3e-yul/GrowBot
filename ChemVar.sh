#! /bin/bash
while true
do
	EC=""
	pH=""
	while [ -z $EC ]
	do
		EC=$(./EC | awk -F" " '{ print $1 }')
	done
	while [ -z $pH ]
	do
		pH=$( ./pH )
	done
	FiveMinVar=$(echo "select (MAX(EC) - MIN(EC))/COUNT(EC) as ECVariance,(MAX(pH) - MIN(pH))/COUNT(pH) as pHVariance from H2O where date >= DATE_SUB(NOW(),INTERVAL 5 MINUTE);" | mysql -upi -pa-51d41e Farm -N)
	ThirMinVar=$(echo "select (MAX(EC) - MIN(EC))/COUNT(EC) as ECVariance,(MAX(pH) - MIN(pH))/COUNT(pH) as pHVariance from H2O where date >= DATE_SUB(NOW(),INTERVAL 30 MINUTE);"| mysql -upi -pa-51d41e Farm -N)
	TwoHourVar=$(echo "select (MAX(EC) - MIN(EC))/COUNT(EC) as ECVariance,(MAX(pH) - MIN(pH))/COUNT(pH) as pHVariance from H2O where date >= DATE_SUB(NOW(),INTERVAL 2 HOUR );"| mysql -upi -pa-51d41e Farm -N)
	clear
	date '+%d-%m-%y %H:%M:%S'
	echo ""
	echo ""
	echo -e "\t EC: "$EC"  pH: "$pH
	echo ""
	echo -e "Period \t ECVariance pHVariance"
	echo -e "5Min \t" $FiveMinVar
	echo -e "30Min \t" $ThirMinVar
	echo -e "120Min \t" $TwoHourVar
	sleep 3
done
