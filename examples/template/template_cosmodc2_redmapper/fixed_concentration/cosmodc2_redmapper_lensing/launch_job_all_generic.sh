#!/usr/bin/bash
$BATCH_ALL

module load conda
export HDF5_DO_MPI_FILE_SYNC=0
#export PYTHONPATH=/sps/lsst/groups/clusters/cl_pipeline_project/TXPipe:$PYTHONPATH
conda activate $CONDA_DIRECTORY/conda_envs/txpipe_clp
export PYTHONPATH=../../../../:$PYTHONPATH
export PYTHONPATH=$TXPIPE_DIRECTORY:$PYTHONPATH

cd $COMPUTATIONDIR

ceci TXPipe.yml
ceci TJPCov.yml

conda deactivate
conda activate $CONDA_DIRECTORY/conda_envs/firecrown_developer_clp
export PYTHONPATH=../../../../:$PYTHONPATH

ceci Firecrown.yml

cd $OUTPUTDIR
cosmosis cluster_counts_mean_mass_redshift_richness.ini
