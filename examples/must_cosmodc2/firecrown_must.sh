#!/usr/bin/bash
conda activate /mustfs/CONTAINERS/conda/lsst/txpipe_clp
conda list
export HDF5_DO_MPI_FILE_SYNC=0
export PYTHONPATH=/mustfs/CONTAINERS/conda/lsst/TXPipe:$PYTHONPATH
export PYTHONPATH=../../:$PYTHONPATH
export PYTHONPATH=/sps/lsst/groups/clusters/cl_pipeline_project/TXPipe/txpipe/extensions/cluster_counts/:$PYTHONPATH
ceci CL_cosmoDC2-full_concat_in2p3.yml --yamlId TXPipe
ceci CL_cosmoDC2-full_concat_in2p3.yml --yamlId TJPCov
conda deactivate
conda activate /mustfs/CONTAINERS/conda/lsst/firecrown_clp
export PYTHONPATH=../../:$PYTHONPATH
ceci CL_cosmoDC2-full_concat_in2p3.yml --yamlId Firecrown
#cd outputs
#cosmosis cluster_counts_mean_mass_redshift_richness.ini

