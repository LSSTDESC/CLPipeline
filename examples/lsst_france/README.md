# LSST France Examples
In these folder, you will find two examples of the Cluster Pipeline run with
the redMaPPer cosmoDC2 catalog. These examples are meant to work only in the
CCIN2P3, since some data files are stored in the computer center. The cluster
catalog was already ingested and saved. To check the data files and output files,
check `/sps/lsst/groups/clusters/cl_pipeline_project/TXPipe_data/cosmodc2/`.

## Generating Shear Catalog
To generate the cluster catalog data, the notebook `generate-440deg2-sample.ipynb`
has the needed code. In there you will find a dry run of a stage in TXPipe that
ingests the cosmoDC2 galaxy shear catalog from GCR and mimics a metacal calibration
stage with the predicted magnitude depths of LSST. 

## Examples
In both examples, we are running the Cluster Pipeline with cluster number counts
and the delta sigma shear profile. We are fitting the scaling relation of the 
mass-richness relation, using the fiducial cosmology values and completeness
and purity fitted with the simulated catalog.

In these folders, you will find the configuration files to run the Pipeline.
- `CL_cosmoDC2-full_concat_in2p3.yml`: This is the pipeline configuration file that sets which stages shall be run and with which configurations.
- `cosmodc2_config_in2p3.yml`: This is the configuration file for each stage run in the pipeline configuration file
- `launch_job_in2p3.sh`: This is the bash script to be submitted where we activate the right conda environments to run each stage of the pipeline.
- `launch_job_firecrown.sh`: Another script to launch the MCMC sampler.

To run the pipeline, simply run:
```
sbatch lauch_job_in2p3.sh
```
This will run the `TXPipe`, `TJPCov` and `Firecrown` stages, generating all
the needed files for the MCMC sampling. After this step, to run the chains,
do:
```
sbatch launch_job_firecrown.sh
```
.

### Cosmodc2 Scaling Relation
In this example, we are using the true shear and the true redshift for the sources from the cosmoDC2 galaxy catalog.

### Cosmodc2 Scaling Relation False
In this example, we are using calibrated shear done in the ingest phase of TXPipe. Also, we are using the magnitudes of the catalog to infer the redshift of the sources using the BPZlite algorithm. The title false relates to the options in the configuration where we choose:
```
true_shear = False
true_redshift = False
```
.
