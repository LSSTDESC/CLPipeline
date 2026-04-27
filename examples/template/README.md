###This script was developed to simplify the configuration of the analysis pipeline's files and ensure their consistency.

It consists in defining a set of configuration parameters (in a `configuration.xml` file) that can be used to parametrize any file used in the analysis pipeline (config files, job submission script, txpipe, firecrown or tjpcov files).  


### >> `Configuration.yml` file

Each key defined in the `configutation.xml` file will be initialized as a parameter that can be used in the definition of any file.

For example :

	##### Run parameters
	site: in2p3
	runidentifier: 20deg2
	
	# Mandatory parameters - these are used to configure properly the computing directories
	#   - name :
	#   - templatedir :  directory that contains the template files
	#   - computingdir :  directory that contains all the templates files once they are fully configured
	#                             all the jobs and batch jobs are to be launched from this directory
	#                             all the output and log files are stored in this directory
	#            CAUTION : the name of this directory shoul dbe self-explanatory and define a different name for each run
	
	name: cosmodc2_$SITE_$RUNIDENTIFIER
	templatedir: template_readme_example/input
	computationdir: $PWD/$NAME
	
	##### job concatenated yaml file : file that contains all the yaml files defined as a yaml multiple document file
	jobconcatyamlfile: $TEMPLATEDIR/job_cosmoDC2-$RUNIDENTIFIER_concat_$SITE.yml
	
	##### Survey data
	data: cosmodc2
	datadir: cosmodc2/$RUNIDENTIFIER
	
	##### Pipeline setup - the parameter value will be defined depending on the "site" parameter value
	txpipe_datadir:
		nersc: /global/cfs/projectdirs/lsst/groups/CL/cl_pipeline_project/TXPipe_data
		in2p3: /sps/lsst/groups/clusters/cl_pipeline_project/TXPipe_data
	
	...
	# Batch parameters 
	batch_id: cosmodc2-$RUNIDENTIFIER
	batch_param_file: ./$TEMPLATEDIR/batch_param.yml
	batch_files: 
    		nersc: ./$TEMPLATEDIR/launch_job_all_generic.sh
    		in2p3: ./$TEMPLATEDIR/launch_txpipe_generic.sh;./$TEMPLATEDIR/launch_fire_generic.sh;./$TEMPLATEDIR/launch_job_all_generic.sh
	

will setup a set of parameters that can be used in any file used to prepare the run.<br>
For each parameter defined in `configuration.yml`, a variable name $PARAMETER_NAME


	$SITE = in2p3
	$RUNIDENTIFIER = 20deg2
	$NAME=cosmodc2_in2p3_20deg2
	$TEMPLATEDIR=template_cosmodc2
	 ...
	$TXPIPE\_DATADIR=/sps/lsst/groups/clusters/cl_pipeline_project/TXPipe_data   = dictionnary are read following the $SITE value
	...
	

**It is possible to add/remove parameters in `configuration.yaml` depending on the type of pipeline to configure.  **
	
### >> ceci yaml files

The yaml files used to define the different ceci pipeline processes are concatenated in an unique file using the yaml multiple document feature  ( files are separated using a `---`). <br>
The name of this concatenated file is defined as *jobconcatyamlfile*  in `configuration.yml`<br>
This yaml file is going to be parametrized based on the values defines in `configuration.yml` and the split into smalled ymal files based on the "id" defined in each section.<br>

In our example, the file `template_readme_example/input/job_cosmoDC2-20deg2_concat.yml` is going to be split into 3 subfiles : `txpipe.yml, firecrown.yml and tjpcov.yml`

	
### >> `batch_param.yml` file	
	
Instead of redefining the batch parameters  ( CPU, RAM, tasks, ....)  for each job, one can store them in a `batch_param.yml` file and retrieve and configure the batch scripts automatically
For example : 
	
	id : cosmodc2-20deg2
	
	# Batch parameters
	batch_txpipe: 
	    nersc: 
	    in2p3: --time=3:00:00;--partition=hpc,lsst;--ntasks=60;--cpus-per-task=1;--mem=128gb;--nodes=1
	batch_all:
	    nersc: -A m1727;-C cpu;--qos=debug;--time=00:30:00;--nodes=1;--ntasks-per-node=32
	    in2p3: --time=1:00:00;--partition=hpc;--ntasks=30;--cpus-per-task=1;--mem=64gb
	
	---
	
	id : cosmodc2-full
	
	...

These will for example  define 2 values  `$BACTH_TXPIPE and $BATCH_ALL` that can be used to configure automatically the job submission scripts.
( see `input/launch_job_all_generic.sh` )
	
### >> creation and initialization of the run files	
	
#### --- configuration command

	python configure_pipeline.py template_readme_example/input/configuration.py


#### --- where are the output files

the configured output files are all stored in the $COMPUTINGDIR directory defined in the `configuration.yml` file.<br>


#### --- how to overwrite a value defined in the `configuration.tml` file

It is possible to overwrite parameters defined in `configuration.yml` by adding a dictionnary of values at the end of the command line.<br> 
For example :

	python3 configure_pipeline.py template_readme_example/input/configuration.py  '{"site":"nersc","runidentifier":"full"}'

will overwrite the "site" and "runidentifier" parameters defined in `configuration. yaml`


