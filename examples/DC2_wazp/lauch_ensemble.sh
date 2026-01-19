#!/usr/bin/bash
#SBATCH --time=20:00:00
#SBATCH --partition=hpc
#SBATCH --ntasks=10
#SBATCH --cpus-per-task=1
#SBATCH --mem=500gb   
#SBATCH --nodes=1

module unload Programming_Languages/anaconda
module load conda
#source /pbs/throng/lsst/software/desc/common/miniconda/setup_current_python.sh
conda activate /sps/lsst/groups/clusters/cl_pipeline_project/conda_envs/txpipe_clp
export HDF5_DO_MPI_FILE_SYNC=0
export PYTHONPATH=/sps/lsst/users/ebarroso/TXPipe:$PYTHONPATH
export PYTHONPATH=../../:$PYTHONPATH

mpirun -n 10 python3 -m txpipe CLClusterEnsembleProfiles   --cluster_catalog_tomography=/sps/lsst/groups/clusters/cl_pipeline_project/TXPipe_data/dc2/outputs//cluster_catalog_tomography.hdf5   --fiducial_cosmology=/sps/lsst/groups/clusters/cl_pipeline_project/TXPipe_data/cosmodc2/fiducial_cosmology.yml   --cluster_shear_catalogs=/sps/lsst/groups/clusters/cl_pipeline_project/TXPipe_data/dc2/outputs//cluster_shear_catalogs.hdf5   --config=./cosmodc2_config_in2p3.yml   --cluster_profiles=/sps/lsst/groups/clusters/cl_pipeline_project/TXPipe_data/dc2/outputs_test/cluster_profiles.pkl --mpi
