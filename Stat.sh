#! /bin/bash

gpio -g mode 26 out
gpio -g mode 20 out
main=$(gpio -g read 26)
light=$(gpio -g read 21)
pump=$(gpio -g read 12)
fan=$(gpio -g read 16)
bubl=$(gpio -g read 20)
status=$light$pump$fan$bubl
#echo $status
if [[ $status -gt 0 ]]
then
#	echo "'"$status"'"
	case $status in
		0001)
			echo -e "\nBubler is on"
		;;

                0010)
                        echo -e "\nfan is on"
                ;;
                0011)
			echo -e "\nfan is on"
                        echo -e "Bubler is on"
                ;;

                0100)
                        echo -e "\npump is on"
                ;;
                0101)
			echo -e "\npump is on"
                        echo -e "Bubler is on"
                ;;

                0110)
			echo -e "\npump is on"
                        echo -e "fan is on"
                ;;
                0111)
			echo -e "\npump is on"
			echo -e "fan is on"
                        echo -e "Bubler is on"
                ;;

                1000)
                        echo -e "\nLight is on"
                ;;
                1001)
			echo -e "\nLight is on"
                        echo -e "Bubler is on"
                ;;

                1010)
			echo -e "\nLight is on"
                        echo -e "fan is on"
                ;;
                1011)
			echo -e "\nLight is on"
			echo -e "fan is on"
                        echo -e "Bubler is on"
                ;;

                1100)
			echo -e "\nLight is on"
                        echo -e "pump is on"
                ;;
                1101)
			echo -e "\nLight is on"
			echo -e "pump is on"
                        echo -e "Bubler is on"
                ;;

                1110)
			echo -e "\nLight is on"
			echo -e "pump is on"
                        echo -e "fan is on"
                ;;
                1111)
			echo -e "\nLight is on"
			echo -e "pump is on"
			echo -e "fan is on"
                        echo -e "Bubler is on"
                ;;
		*)
			echo -e "unknown"
    		;;
	esac
else
	echo -e "\nAll is OFF" 
fi
echo -e "\n"
