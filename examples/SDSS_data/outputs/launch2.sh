#!/usr/bin/bash
#SBATCH --time=05:00:00
#SBATCH --partition=hpc,lsst
#SBATCH --cpus-per-task=1
#SBATCH --mem=128000

source ~/.bashrc
export HDF5_DO_MPI_FILE_SYNC=0
conda activate firecrown_clp
export PYTHONPATH=${CLP_DIR}:$PYTHONPATH
cosmosis cluster_counts_mean_mass_redshift_richness.ini
