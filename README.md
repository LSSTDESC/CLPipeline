# CLPipeline
Repository devoted to the Cluster working group from the DESC-LSST collaboration

## Instalation
To create both Firecrown and TXPipe conda enviroments, run: 
```
conda env update -f txpipe_enviroment.yml
conda activate txpipe_clp
pip install git+https://github.com/hellebore74/ceci
conda deactivate
conda env update -f firecrown_enviroment.yml
conda activate firecrown_clp
conda env config vars set CSL_DIR=${CONDA_PREFIX}/cosmosis-standard-library CLP_DIR=${PWD}
pip install git+https://github.com/hellebore74/ceci
conda deactivate
conda activate firecrown_clp
cd ${CONDA_PREFIX}
source ${CONDA_PREFIX}/bin/cosmosis-configure
cosmosis-build-standard-library main
```
To activate one or the other enviroment, run:
```
conda activate firecrown_cpl
```
or
```
conda activate txpipe_cpl
```
## Example run
Inside the repository folder, run the bash script or
```
ceci tests/CL_test_txpipe_concat.yml --yamlId Firecrown
```
with the yamlId being either `TJPCov` or `Firecrown`. DO NOT RUN WITH TXPIPE 
OUTSIDE THE BASHSCRIPT. The TXPipe run requries parallell jobs and several computing
nodes, which is not possible to be ran locally.

