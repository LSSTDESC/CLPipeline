


This script was developed to simplify the configuration of the analysis pipeline's files and ensure their consistency.

It consists in defining a set of configuration parameters (in a configuration.xml file) that can be used to parametrize any file used in the analysis pipeline (config files, job submission script, txpipe, firecrown or tjpcov files).  

Each key defined in the configutation.xml file will be initialized as a parameter that can be used in the definition of any file.

For exemple (see template_cosmodc2/configuration.yaml :

site: in2p3

# Directory that will contain all the files
runidentifier: 20deg2

name: cosmodc2_$SITE_$RUNIDENTIFIER
templatedir: template_cosmodc2
computationdir: $PWD/$NAME

# job concatenated yaml file
jobconcatyamlfile: $TEMPLATEDIR/job_cosmoDC2-$RUNIDENTIFIER_concat_$SITE.yml

# Survey data
data: cosmodc2
datadir: cosmodc2/$RUNIDENTIFIER

# Pipeline setup
txpipe_datadir:
    nersc: /global/cfs/projectdirs/lsst/groups/CL/cl_pipeline_project/TXPipe_data
    in2p3: /sps/lsst/groups/clusters/cl_pipeline_project/TXPipe_data
    local: my_data_directory

will setup the following paramater:

$SITE = in2p3
$RUNIDENTIFIER = 20deg2
$NAME=cosmodc2_in2p3_20deg2
$TEMPLATEDIR=template_cosmodc2
...
$TXPIPE_DATADIR=/sps/lsst/groups/clusters/cl_pipeline_project/TXPipe_data   => dictionnary are read following the $SITE value
...

All these configurations values are automatically used to setup the yml and sh files accordingly
( see template_cosmodc2/job_cosmoDC2-full_concat_in2p3.yml or template_cosmodc2/cosmodc2_config_full.yml, )





It is possible to overwrite a parameter defined in configuration.yml by adding a dictionnary of values at the end of the command line. For exemple :

python3 configure_pipeline.py template_cosmodc2_redmapper/fixed_concentration/cosmodc2_redmapper_full_analysis/configuration.yml '{"runidentifier":"mor"}'
python3 configure_pipeline.py template_cosmodc2_redmapper/fixed_concentration/cosmodc2_redmapper_full_analysis/configuration.yml '{"runidentifier":"cosmo"}'
python3 configure_pipeline.py template_cosmodc2_redmapper/fixed_concentration/cosmodc2_redmapper_full_analysis/configuration.yml '{"runidentifier":"both"}'
