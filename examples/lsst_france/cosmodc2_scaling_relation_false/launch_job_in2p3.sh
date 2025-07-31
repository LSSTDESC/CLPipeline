#!/usr/bin/bash
#SBATCH --time=23:00:00
#SBATCH --partition=hpc,lsst
#SBATCH --cpus-per-task=1
#SBATCH --mem=600gb   
#SBATCH --ntasks=30

source /pbs/throng/lsst/software/desc/common/miniconda/setup_current_python.sh
conda activate /sps/lsst/groups/clusters/cl_pipeline_project/conda_envs/txpipe_clp
export HDF5_DO_MPI_FILE_SYNC=0
export PYTHONPATH=/sps/lsst/groups/clusters/cl_pipeline_project/TXPipe:$PYTHONPATH
export PYTHONPATH=../../../:$PYTHONPATH
export PATH=/sps/lsst/groups/clusters/cl_pipeline_project/conda_envs/txpipe_clp/bin:$PATH
export PYTHONPATH=/sps/lsst/groups/clusters/cl_pipeline_project/TXPipe/txpipe/extensions/cluster_counts/:$PYTHONPATH
ceci CL_cosmoDC2-full_concat_in2p3.yml --yamlId TXPipe
ceci CL_cosmoDC2-full_concat_in2p3.yml --yamlId TJPCov
conda deactivate
conda activate /sps/lsst/groups/clusters/cl_pipeline_project/conda_envs/firecrown_clp
export PYTHONPATH=../../:$PYTHONPATH
export PATH=/sps/lsst/groups/clusters/cl_pipeline_project/conda_envs/firecrown_clp/bin:$PATH
ceci CL_cosmoDC2-full_concat_in2p3.yml --yamlId Firecrown
#cd outputs
#cosmosis cluster_counts_mean_mass_redshift_richness.ini

