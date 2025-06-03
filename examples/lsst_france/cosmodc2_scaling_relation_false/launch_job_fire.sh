#!/usr/bin/bash

#SBATCH --time=15:00:00
#SBATCH --partition=lsst
#SBATCH --mem=8gb
#SBATCH --job-name=cosmosis_emcee
#SBATCH --ntasks=8

# Set your project path
export PYTHONPATH=/sps/lsst/users/ebarroso/CLPipeline/:$PYTHONPATH
# Run CosmoSIS
cd outputs

cosmosis cluster_counts_mean_mass_redshift_richness.ini

