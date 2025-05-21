#!/usr/bin/bash
#SBATCH --time=13:00:00
#SBATCH --partition=hpc,lsst
#SBATCH --ntasks=30
#SBATCH --cpus-per-task=1
#SBATCH --mem=600gb   
#SBATCH --nodes=1

module load conda
#source /pbs/throng/lsst/software/desc/common/miniconda/setup_current_python.sh
conda activate /sps/lsst/groups/clusters/cl_pipeline_project/conda_envs/txpipe_clp
export HDF5_DO_MPI_FILE_SYNC=0
export PYTHONPATH=/sps/lsst/groups/clusters/cl_pipeline_project/TXPipe:$PYTHONPATH
export PYTHONPATH=../../../:$PYTHONPATH
export PATH=/sps/lsst/groups/clusters/cl_pipeline_project/conda_envs/txpipe_clp/bin:$PATH
ceci CL_txpipe_shear_in2p3.yml --yamlId TXPipe
