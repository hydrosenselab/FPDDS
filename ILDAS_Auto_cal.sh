#!/usr/bin/env bash
#PBS -N Auto_Ncal_imd
#PBS -P ildas.spons
#PBS -m bea
#PBS -M cez218606@iitd.ac.in
#PBS -l select=1:ncpus=16:mpiprocs=16:mem=180gb
#PBS -l walltime=150:05:00
#PBS -q standard
#PBS -o /home/civil/phd/cez218606/Auto_calibration/Final/Narmada_FPDDS11/logs/output_final.txt
#PBS -e /home/civil/phd/cez218606/Auto_calibration/Final/Narmada_FPDDS11/logs/error_final.txt

# Environment
echo "==============================="
echo $PBS_JOBID
cat $PBS_NODEFILE
cat $PBS_NTASKS
echo "==============================="

cd /home/civil/phd/cez218606/Auto_calibration/Final/Narmada_FPDDS11/
~/anaconda3/envs/geo_env/bin/python /home/civil/phd/cez218606/Auto_calibration/Final/Narmada_FPDDS11/FPDDS/Scripts/notebooks/Model_run.py

exit 0
