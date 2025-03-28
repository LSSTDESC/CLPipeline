# CLPipeline
Repository dedicated to the Cluster Working Group from the DESC-LSST collaboration.

## Installation
To run the examples, there is no need to install/create new conda environments.
The environments are saved in a shared space both in in2p3 and Nersc. For the 
moment, we have two conda environments. One for Firecrown and another one for
TXPipe and TJPCov. For firecrown, run:
```
conda activate /sps/lsst/groups/clusters/cl_pipeline_project/conda_envs/firecrown_clp
```
for in2p3 and 
```
```

for Nersc.

For TXPipe and TJPCov,
```
conda activate /sps/lsst/groups/clusters/cl_pipeline_project/conda_envs/txpipe_clp
```
for in2p3 and 
```
```
for Nersc.

To have these same environments locally,run:
```
conda env update -f txpipe_environment.yml
conda env update -f firecrown_environment.yml
conda activate firecrown_clp
conda env config vars set CSL_DIR=${CONDA_PREFIX}/cosmosis-standard-library
conda deactivate
conda activate firecrown_clp
cd ${CONDA_PREFIX}
source ${CONDA_PREFIX}/bin/cosmosis-configure
cosmosis-build-standard-library main
```
To activate one or the other environment, run:
```
conda activate firecrown_clp
```
or
```
conda activate txpipe_clp
```

## Mock Example Run
Inside the repository folder, run:
```
conda activate /sps/lsst/groups/clusters/cl_pipeline_project/conda_envs/firecrown_clp
ceci tests/CL_test_txpipe_concat.yml --yamlId Firecrown
```
with `yamlId` being either `TJPCov` or `Firecrown`. **DO NOT RUN TXPipe** outside
the bash script. TXPipe requires parallel jobs and multiple computing nodes, which
cannot be run locally. The `yamlId` variable defines wich part of the pipeline will
run.

## Example Runs
Inside the `examples` repository folder, there are three different examples:
`cosmoDC2-20deg2`, `SDSS_data`, and `Wazp_cosmoDC2`. Each example is configured
through two files:

1. `CL_concat.yml` - Defines which pipeline stages should be run, specifies
inputs and outputs, and manages parallelization and computation settings.
2. `config.yml` - Contains configuration details for each stage. Any modeling
changes should be made in this file.

### cosmoDC2-20deg2
This folder contains `CL_cosmoDC2-20deg2_concat_in2p3.yml` and
`CL_cosmoDC2-20deg2_concat_nersc.yml`, the pipeline configuration files for
the `in2p3` and `nersc` computing centers. The `cosmodc2_config_in2p3.yml` and 
`cosmodc2_config_nersc.yml` files defines the configuration for each stage.
Outputs are stored in `cosmoDC2-20deg2/outputs`.

To run this example, ensure the conda environments defined in
`firecrown_environment.yml` and `txpipe_environment.yml` are installed. Then,
inside `cosmoDC2-20deg2`, run:
```
sbatch launch_job_in2p3.sh
```
for `in2p3` and
```
sbatch launch_job_nersc.sh
```
for `nersc`.

This example runs three pipeline stages:
1. `TXPipe` processes the 20deg2 files from `cosmoDC2`, handling calibration,
binning, and computations, producing a `Sacc` file.
2. `TJPCov` computes the theoretical covariance and updates the `Sacc` file.
3. `Firecrown` generates necessary files for MCMC sampling, defining the
Firecrown likelihood with the `Sacc` file as input.

Finally, `cosmosis` is executed to start MCMC sampling. The final chain plot
can be found in `examples/plot_samples.ipynb`.

### wazp_cosmoDC2
This folder contains `CL_cosmoDC2_wazp_concat.yml`, the pipeline configuration 
file. The `cosmodc2_config.yml` file defines all stage configurations.

To run this example, inside
`wazp_cosmoDC2`, for in2p3 run:
```
conda activate /sps/lsst/groups/clusters/cl_pipeline_project/conda_envs/firecrown_clp
python generate_wazp_sacc_cosmodc2.py
```
and for nersc:
```
conda activate /sps/lsst/groups/clusters/cl_pipeline_project/conda_envs/firecrown_clp
python generate_wazp_sacc_cosmodc2.py
```
This generates the required `Sacc` file. Then run:
```
sbatch launch_job_in2p3.sh
```
for `in2p3` and
```
sbatch launch_job_nersc.sh
```
for `nersc`.

This example runs the `TJPCov` and `Firecrown` stages:
1. `TJPCov` computes theoretical covariance and updates the `Sacc` file.
2. `Firecrown` generates necessary files for MCMC sampling.

To run the example with a data-driven covariance, use:
```
conda activate firecrown_clp
python generate_wazp_sacc_cosmodc2.py
sbatch launch_fire.sh
```
.

The final chain plot is in `examples/plot_samples.ipynb`.

### SDSS_data
This folder contains `CL_SDSS_concat.yml`, the pipeline configuration file.
This file define stages, inputs, and outputs. Results are stored in `SDSS_data/outputs`.

To run this example, inside `SDSS_data`, for in2p3 run:

```
conda activate /sps/lsst/groups/cluster/cl_pipeline_project.conda_envs/firecrown_clp
python generate_sdss_data.py
```
and for nersc:
```
conda activate /sps/lsst/groups/clusters/cl_pipeline_project/conda_envs/firecrown_clp
python generate_wazp_sacc_cosmodc2.py
```

This generates the required `Sacc` file. Then run:
```
sbatch launch_job_in2p3.sh
```
for `in2p3` and
```
sbatch launch_job_nersc.sh
```
for `nersc`.

This example runs only the `Firecrown` stage, generating necessary files for
MCMC sampling. The final chain plot is in `examples/plot_samples.ipynb`.

## Theory Test
Inside `cl_theory_test` there some example notebooks about how to use Firecrown
to make theoretical predictions.
