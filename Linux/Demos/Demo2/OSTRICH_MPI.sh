#!/bin/bash

# select parallel version of input file
cp ostIn_Parallel.txt ostIn.txt

# load modules or set path so that it includes desired mpi launcher
module load lib/intel
#module load intel-mpi

# match assignment to location of OSTRICH installation
OSTRICH_MPI=/home/civil/phd/cez218606/LISF1/Auto_Calibration/Linux/intelmpi/5.1.1/OstrichMPI

export I_MPI_PMI_LIBRARY=/usr/lib64/libpmi.so
mpirun -n 4 $OSTRICH_MPI

# pause for user input
read -n1 -r -p "Press any key to continue..." key

