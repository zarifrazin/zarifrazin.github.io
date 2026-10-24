#!/bin/bash
#BSUB -n 32
#BSUB -R "span[hosts=1]"
#BSUB -W 60
#BSUB -J droplet
#BSUB -o stdout.%J
#BSUB -e stderr.%J

module load lammps/2022Jun23/intel/cpu
mpirun lmp_hazel -in  droplet.lmp
