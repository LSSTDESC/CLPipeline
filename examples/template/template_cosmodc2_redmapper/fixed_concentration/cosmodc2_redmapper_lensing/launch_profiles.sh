#!/usr/bin/bash
$BATCH_PROFILES

module load conda
export HDF5_DO_MPI_FILE_SYNC=0

conda activate $CONDA_DIRECTORY/conda_envs/txpipe_clp

export PYTHONPATH=../../../:$PYTHONPATH
export PYTHONPATH=/sps/lsst/users/ebarroso/TXPipe:$PYTHONPATH #/sps/lsst/groups/clusters/cl_pipeline_project/TXPipe:$PYTHONPATH
ceci TXPipe.yml
