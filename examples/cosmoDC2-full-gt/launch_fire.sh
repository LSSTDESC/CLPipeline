#!/usr/bin/bash
#SBATCH --time=15:00:00
#SBATCH --partition=hpc,lsst
#SBATCH --cpus-per-task=1
#SBATCH --mem=64gb

source ~/.bashrc
conda activate firecrown_clp
export PYTHONPATH=../../:$PYTHONPATH
ceci CL_cosmoDC2-20deg2_concat_in2p3.yml --yamlId Firecrown
cd outputs
cosmosis cluster_counts_mean_mass_redshift_richness.ini
