#!/bin/bash

# set path to OSTRICH binary
OSTRICH=/home/civil/phd/cez218606/LISF1/Auto_Calibration/Linux/intelmpi/5.1.1/Ostrich

# use the serial version of the input file
cp ostIn_Serial.txt ostIn.txt

# initialize counter used by SaveBest.sh
echo 0 > Counter.txt

$OSTRICH

# pause for user input
read -n1 -r -p "Press any key to continue..." key

