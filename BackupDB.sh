#! /bin/bash
mysqldump --databases -pa-51d41e  Farm > ~/$(date +%Y-%m-%d-%H:%M:%S)-Farm.sql
tables=$(echo "show tables" | mysql -upi -pa-51d41e Farm)

for table in $tables
do 
	if [[ $table != "Tables_in_Farm" ]] && [[ $table != "Temps" ]]
	then
		echo "truncate table " $table ";" | mysql -upi -pa-51d41e Farm
		echo $table "backed-up and truncated"
	fi
done
