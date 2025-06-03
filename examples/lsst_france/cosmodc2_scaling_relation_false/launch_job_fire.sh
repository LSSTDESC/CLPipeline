#!/bin/bash
#SBATCH --time=15:00:00
#SBATCH --partition=hpc,lsst
#SBATCH --cpus-per-task=1
#SBATCH --mem=8gb
#SBATCH --ntasks=1
#SBATCH --job-name=cosmosis_emcee
#SBATCH --output=cosmosis_emcee.out
#SBATCH --error=cosmosis_emcee.err

# Load environment
#source ~/.bashrc
#conda activate firecrown_clp

# Set your project path
export PYTHONPATH=/sps/lsst/users/ebarroso/CLPipeline/:$PYTHONPATH

# Run CosmoSIS
cd outputs

cosmosis cluster_counts_mean_mass_redshift_richness.ini

