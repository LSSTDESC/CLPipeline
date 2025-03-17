#!/usr/bin/bash
#SBATCH --time=15:00:00
#SBATCH --partition=hpc,lsst
#SBATCH --cpus-per-task=1
#SBATCH --mem=128000

source ~/.bashrc
conda activate firecrown_clp
export PYTHONPATH=${CLP_DIR}:$PYTHONPATH
ceci CL_cosmoDC2_wazp_concat.yml --yamlId Firecrown
cd outputs
cosmosis cluster_counts_mean_mass_redshift_richness.ini
