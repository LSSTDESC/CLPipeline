#!/usr/bin/bash
#SBATCH --time=05:00:00
#SBATCH --partition=hpc,lsst
#SBATCH --cpus-per-task=1
#SBATCH --mem=128000

source /pbs/throng/lsst/software/desc/common/miniconda/setup_current_python.sh
conda activate /sps/lsst/groups/clusters/cl_pipeline_project/conda_envs/txpipe_clp
export HDF5_DO_MPI_FILE_SYNC=0
export PYTHONPATH=/sps/lsst/groups/clusters/cl_pipeline_project/TXPipe:$PYTHONPATH
export PYTHONPATH=../../:$PYTHONPATH
ceci CL_cosmoDC2-20deg2_concat_in2p3.yml --yamlId TXPipe 
ceci CL_cosmoDC2-20deg2_concat_in2p3.yml --yamlId TJPCov
conda deactivate
conda activate /sps/lsst/groups/clusters/cl_pipeline_project/conda_envs/firecrown_clp
export PYTHONPATH=../../:$PYTHONPATH
ceci CL_cosmoDC2-20deg2_concat_in2p3.yml --yamlId Firecrown
cd outputs
cosmosis cluster_counts_mean_mass_redshift_richness.ini
