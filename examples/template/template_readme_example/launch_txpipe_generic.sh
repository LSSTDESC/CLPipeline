#!/usr/bin/bash
$BATCH_TXPIPE

source ~/.bashrc
#source /pbs/throng/lsst/software/desc/common/miniconda/setup_current_python.sh
conda activate $CONDA_DIRECTORY/conda_envs/txpipe_clp

export HDF5_DO_MPI_FILE_SYNC=0
export PYTHONPATH=$TXPIPE_DIRECTORY:$PYTHONPATH
export PYTHONPATH=../../:$PYTHONPATH

cd $COMPUTINGDIR
ceci TXPipe.yml 
