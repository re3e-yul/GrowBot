#! /bin/bash
if [ $(gpio -g read 18) = '0' ]
then
        echo "Lights Off" 
else
        echo "Lights On"
fi
