#!/usr/bin/bash
#SBATCH --time=15:00:00
#SBATCH --partition=hpc,lsst
#SBATCH --cpus-per-task=1
#SBATCH --mem=8gb

module load conda
#source /pbs/throng/lsst/software/desc/common/miniconda/setup_current_python.sh
conda activate /sps/lsst/groups/clusters/cl_pipeline_project/conda_envs/txpipe_clp
export PYTHONPATH=../../:$PYTHONPATH
ceci CL_cosmoDC2_wazp_concat.yml --yamlId TJPCov
conda deactivate
conda activate /sps/lsst/groups/clusters/cl_pipeline_project/conda_envs/firecrown_clp
export PYTHONPATH=../../:$PYTHONPATH
ceci CL_cosmoDC2_wazp_concat.yml --yamlId Firecrown
cd outputs
cosmosis cluster_counts_mean_mass_redshift_richness.ini
