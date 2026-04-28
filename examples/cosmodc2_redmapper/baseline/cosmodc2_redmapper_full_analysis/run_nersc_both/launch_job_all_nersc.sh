#!/usr/bin/bash
#SBATCH -A m1727
#SBATCH -C cpu
#SBATCH --qos=debug
#SBATCH --time=00:30:00
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=32

module load conda
export HDF5_DO_MPI_FILE_SYNC=0
#export PYTHONPATH=/sps/lsst/groups/clusters/cl_pipeline_project/TXPipe:$PYTHONPATH
conda activate /global/cfs/projectdirs/lsst/groups/CL/cl_pipeline_project/conda_envs/txpipe_clp
export PYTHONPATH=/global/u2/e/edujb/CLPipeline/:$PYTHONPATH
export PYTHONPATH=/global/cfs/projectdirs/lsst/groups/CL/cl_pipeline_project/TXPipe:$PYTHONPATH

cd /sps/lsst/users/ebarroso/CLPipeline/examples/cosmodc2_redmapper/templates/../baseline/cosmodc2_redmapper_full_analysis/run_nersc_both

ceci TXPipe.yml
ceci TJPCov.yml

conda deactivate
conda activate /global/cfs/projectdirs/lsst/groups/CL/cl_pipeline_project/conda_envs/firecrown_developer_clp
export PYTHONPATH=/sps/lsst/users/ebarroso/CLPipeline:$PYTHONPATH

ceci Firecrown.yml

cd ./outputs_both
cosmosis cluster_counts_mean_mass_redshift_richness.ini
