#!/bin/bash
#SBATCH --time=2:00:00
#SBATCH --partition=hpc,lsst
#SBATCH --mem=64gb
#SBATCH --ntasks=1
#SBATCH --job-name=test_emcee_serial
#SBATCH --output=cosmosis_emcee_test.out
#SBATCH --error=cosmosis_emcee_test.err

source /pbs/home/e/ebarroso/.bashrc_ss
conda activate firecrown_clp
unset PYTHONPATH
export PYTHONPATH=/sps/lsst/users/ebarroso/miniforge3/envs/firecrown_clp:$PYTHONPATH
# Set your project path
export PYTHONPATH=/sps/lsst/users/ebarroso/CLPipeline/:$PYTHONPATH
# Run CosmoSIS
cd outputs

cosmosis cluster_counts_mean_mass_redshift_richness.ini

