#!/usr/bin/bash
#SBATCH --time=3:00:00
#SBATCH --partition=hpc,lsst
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=200gb

module load conda
conda activate /sps/lsst/groups/clusters/cl_pipeline_project/conda_envs/txpipe_clp
export HDF5_DO_MPI_FILE_SYNC=0
export PYTHONPATH=/sps/lsst/groups/clusters/cl_pipeline_project/TXPipe/:$PYTHONPATH
ceci pipeline.yml
