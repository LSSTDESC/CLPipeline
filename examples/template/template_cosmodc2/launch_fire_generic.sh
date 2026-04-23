#!/usr/bin/bash
$BATCH_FIRECROWN

module load conda
export PYTHONPATH=../../:$PYTHONPATH
conda activate $CONDA_DIRECTORY/conda_envs/firecrown_developer_clp
export PYTHONPATH=../../:$PYTHONPATH

cd $COMPUTINGDIR
ceci Firecrown.yml
#cd $OUTPUTDIR
#cosmosis cluster_counts_mean_mass_redshift_richness.ini
