#!/bin/bash

# use serial version of input file
cp ostIn_Serial.txt ostIn.txt

# set path to OSTRICH binary
OSTRICH=/home/civil/phd/cez218606/LISF1/Auto_Calibration/Linux/intelmpi/5.1.1/Ostrich

$OSTRICH

# pause for user input
read -n1 -r -p "Press any key to continue..." key

