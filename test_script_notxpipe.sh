#!/usr/bin/bash
#SBATCH --time=05:00:00
#SBATCH --partition=hpc,lsst
#SBATCH --cpus-per-task=1
#SBATCH --mem=128000

source ~/.bashrc
conda activate txpipe_clp 
export HDF5_DO_MPI_FILE_SYNC=0
export PYTHONPATH=/sps/lsst/groups/clusters/cl_pipeline_project/TXPipe:$PYTHONPATH
ceci tests/CL_test_txpipe_concat.yml --yamlId TJPCov
conda deactivate
conda activate firecrown_clp
ceci tests/CL_test_txpipe_concat.yml --yamlId Firecrown
cd tests/outputs
cosmosis cluster_counts_mean_mass_redshift_richness.ini
