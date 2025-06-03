#!/usr/bin/bash
#SBATCH --partition=hpc               # Partition choice
#SBATCH --mem=8G                    # Memory in MB per default
#SBATCH --time 13:00:00             # 7 days by default on htc partition
#SBATCH --cpus-per-task=8
#  SBATCH --ntasks=1
#SBATCH --job-name=cosmosis_emcee
#SBATCH --output=cosmosis_emcee.out
#SBATCH --error=cosmosis_emcee.err
source ~/.bashrc
#source /pbs/throng/lsst/software/desc/common/miniconda/setup_current_python.sh
conda activate firecrown_clp
# Set your project path

# Run CosmoSIS
cd outputs
export PYTHONPATH=/sps/lsst/users/ebarroso/CLPipeline/:$PYTHONPATH
cosmosis cluster_counts_mean_mass_redshift_richness.ini

