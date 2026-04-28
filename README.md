# CLPipeline
Repository dedicated to the Cluster Working Group of the DESC-LSST collaboration.

## Installation
To run the examples, there is no need to create new Conda environments.
Shared environments are available on both IN2P3 and NERSC.

Currently, two environments are provided:
- One for Firecrown
- One for TXPipe and TJPCov

### Firecrown

Activate the Firecrown environment with:

IN2P3:
conda activate /sps/lsst/groups/clusters/cl_pipeline_project/conda_envs/firecrown_clp

NERSC:
conda activate /global/cfs/projectdirs/lsst/groups/CL/cl_pipeline_project/conda_envs/firecrown_clp

### TXPipe and TJPCov

IN2P3:
conda activate /sps/lsst/groups/clusters/cl_pipeline_project/conda_envs/txpipe_clp

NERSC:
conda activate /global/cfs/projectdirs/lsst/groups/CL/cl_pipeline_project/conda_envs/txpipe_clp

---

### Local Installation

To reproduce these environments locally, run:

conda env update -f txpipe_environment.yml
conda env update -f firecrown_environment.yml

conda activate firecrown_clp
conda env config vars set CSL_DIR=${CONDA_PREFIX}/cosmosis-standard-library

conda deactivate
conda activate firecrown_clp

cd ${CONDA_PREFIX}
source ${CONDA_PREFIX}/bin/cosmosis-configure
cosmosis-build-standard-library main

To switch between environments:

conda activate firecrown_clp

or

conda activate txpipe_clp

---

## Pipeline Structure

This repository connects:
- TXPipe for data computation
- TJPCov for covariance matrix computation
- Firecrown for MCMC inference

The pipeline is managed using Ceci.

To run the pipeline, two configuration files are required:

1. CL_concat.yml  
   Defines which pipeline stages are executed, specifies inputs and outputs, and manages parallelization and computation settings.

2. config.yml  
   Contains configuration details for each stage. Any modeling changes should be made in this file.

The pipeline configuration file defines:
- Which stages are run
- Input and output files
- Whether MPI is used
- Other global settings

The stage configuration file defines parameters specific to each stage.

We use separate configurations for TXPipe, TJPCov, and Firecrown because:
- They produce different outputs
- They require different Conda environments

Pipeline flow:
- TXPipe performs data computation and outputs a SACC file
- TJPCov updates this file with the covariance matrix
- Firecrown prepares the inputs required for inference

A separate job must be run to execute the final Firecrown inference.

Note:
Due to missing components in TJPCov, the Firecrown stage currently performs additional computations to rescale the covariance matrix.

---

## Example Runs

The `examples` directory contains sample pipeline executions.

In `examples/cosmodc2_remapper`, there are multiple example analyses.
There is also a template directory (`examples/template`) with scripts to generate the required files.
However, using the template is optional if you are familiar with manually constructing the pipeline inputs, as shown in `examples/cosmodc_halos`.

After generating the necessary files, run the pipeline using Ceci.

Example:
examples/cosmodc2_remapper/baseline/run_in2p3_mor

## Scripts
Check `examples/template` on how to use a script to generate the pipeline and configuration files. Note that this was implementes for cosmodc2 and it is under construction for further analysis.