#!/usr/bin/bash
#SBATCH --time=7:00:00
#SBATCH --partition=hpc,lsst
#SBATCH --cpus-per-task=1
#SBATCH --mem=640gb
#SBATCH --ntasks=60 
module load conda
export HDF5_DO_MPI_FILE_SYNC=0
#export PYTHONPATH=/sps/lsst/groups/clusters/cl_pipeline_project/TXPipe:$PYTHONPATH
conda activate /sps/lsst/groups/clusters/cl_pipeline_project/conda_envs/txpipe_clp
export PYTHONPATH=../../../:$PYTHONPATH
export PYTHONPATH=/sps/lsst/groups/clusters/cl_pipeline_project/TXPipe:$PYTHONPATH
ceci CL_cosmoDC2-020_080.yml --yamlId TXPipe