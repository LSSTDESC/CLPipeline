#!/usr/bin/bash
#SBATCH --time=13:00:00
#SBATCH --partition=lsst
#SBATCH --ntasks=60
#SBATCH --cpus-per-task=1
#SBATCH --mem=400gb   
#SBATCH --nodes=1

source ~/.bashrc
#source /pbs/throng/lsst/software/desc/common/miniconda/setup_current_python.sh
conda activate txpipe_clp
export HDF5_DO_MPI_FILE_SYNC=0
export PYTHONPATH=/sps/lsst/groups/clusters/cl_pipeline_project/TXPipe:$PYTHONPATH
export PYTHONPATH=../../:$PYTHONPATH
ceci CL_cosmoDC2-full_concat_in2p3.yml --yamlId TXPipe 
