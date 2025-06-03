#!/usr/bin/bash
#SBATCH --partition=hpc,lsst               # Partition choice
#SBATCH --mem=8G                    # Memory in MB per default
#SBATCH --time 13:00:00             # 7 days by default on htc partition
#SBATCH --cpus-per-task=1
#SBATCH --ntasks=1
#SBATCH --job-name=cosmosis_emcee
#SBATCH --output=cosmosis_emcee.out
#SBATCH --error=cosmosis_emcee.err

module load Programming_Languages/anaconda/3.11
#source ~/.bashrc
#source /pbs/throng/lsst/software/desc/common/miniconda/setup_current_python.sh
conda activate /sps/lsst/users/ebarroso/miniforge3/envs/firecrown_clp
# Set your project path
export OMP_NUM_THREADS=1
pip list emcee
# Run CosmoSIS
cd outputs
export PYTHONPATH=/sps/lsst/users/ebarroso/CLPipeline/:$PYTHONPATH
cosmosis cluster_counts_mean_mass_redshift_richness.ini

