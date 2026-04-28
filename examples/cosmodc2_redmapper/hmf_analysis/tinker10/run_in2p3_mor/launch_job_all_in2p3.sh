#!/usr/bin/bash
#SBATCH --time=15:00:00
#SBATCH --partition=hpc,lsst
#SBATCH --cpus-per-task=1
#SBATCH --mem=80gb
#SBATCH --ntasks=30

module load conda
export HDF5_DO_MPI_FILE_SYNC=0
#export PYTHONPATH=/sps/lsst/groups/clusters/cl_pipeline_project/TXPipe:$PYTHONPATH
conda activate /sps/lsst/groups/clusters/cl_pipeline_project/conda_envs/txpipe_clp
export PYTHONPATH=/sps/lsst/users/ebarroso/CLPipeline:$PYTHONPATH
export PYTHONPATH=/sps/lsst/groups/clusters/cl_pipeline_project/TXPipe:$PYTHONPATH

cd /sps/lsst/users/ebarroso/CLPipeline/examples/cosmodc2_redmapper/templates/../hmf_analysis/tinker10/run_in2p3_mor

ceci TXPipe.yml

conda deactivate
conda activate /sps/lsst/groups/clusters/cl_pipeline_project/conda_envs/firecrown_developer_clp
export PYTHONPATH=/sps/lsst/users/ebarroso/CLPipeline:$PYTHONPATH

ceci TJPCov.yml
ceci Firecrown.yml

cd ./outputs_mor
cosmosis cluster_counts_mean_mass_redshift_richness.ini
