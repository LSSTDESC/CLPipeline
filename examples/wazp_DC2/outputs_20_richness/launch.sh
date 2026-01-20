#!/usr/bin/bash
#SBATCH --time=15:00:00
#SBATCH --partition=hpc,lsst
#SBATCH --cpus-per-task=1
#SBATCH --mem=16gb

source ~/.bashrc
conda activate firecrown_clp
cosmosis cluster_counts_mean_mass_redshift_richness.ini
