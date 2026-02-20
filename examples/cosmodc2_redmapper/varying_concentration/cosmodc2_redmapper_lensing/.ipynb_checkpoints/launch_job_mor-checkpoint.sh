#!/usr/bin/bash
#SBATCH --time=15:00:00
#SBATCH --partition=hpc,lsst
#SBATCH --cpus-per-task=1
#SBATCH --mem=8gb
#SBATCH --ntasks=1 
module load conda
export HDF5_DO_MPI_FILE_SYNC=0
conda activate /sps/lsst/groups/clusters/cl_pipeline_project/conda_envs/txpipe_clp
export PYTHONPATH=../../../../:$PYTHONPATH
export PYTHONPATH=/sps/lsst/users/ebarroso/TXPipe:$PYTHONPATH #/sps/lsst/groups/clusters/cl_pipeline_project/TXPipe:$PYTHONPATH
ceci CL_cosmoDC2-full_concat_mor.yml --yamlId TXPipe
ceci CL_cosmoDC2-full_concat_mor.yml --yamlId TJPCov
conda deactivate
conda activate /sps/lsst/groups/clusters/cl_pipeline_project/conda_envs/firecrown_developer_clp
export PYTHONPATH=../../../../:$PYTHONPATH
ceci CL_cosmoDC2-full_concat_mor.yml --yamlId Firecrown
cd outputs_mor
cosmosis cluster_counts_mean_mass_redshift_richness.ini
