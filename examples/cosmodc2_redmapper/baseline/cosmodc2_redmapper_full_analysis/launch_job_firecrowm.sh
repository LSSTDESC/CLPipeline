#!/usr/bin/bash
#SBATCH --time=15:00:00
#SBATCH --partition=hpc,lsst
#SBATCH --cpus-per-task=1
#SBATCH --mem=8gb
#SBATCH --ntasks=10 
module load conda
export HDF5_DO_MPI_FILE_SYNC=0
conda activate /sps/lsst/groups/clusters/cl_pipeline_project/conda_envs/firecrown_developer_clp
export PYTHONPATH=../../../:$PYTHONPATH
cd outputs_mor
cosmosis cluster_counts_mean_mass_redshift_richness.ini
