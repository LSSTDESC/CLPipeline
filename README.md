# CLPipeline
Repository devoted to the Cluster working group from the DESC-LSST collaboration

To create both Firecrown and TXPipe conda enviroments, run: 
```
conda env update -f firecrown_enviroment.yml
conda activate firecrown_clp
conda env config vars set CSL_DIR=${CONDA_PREFIX}/cosmosis-standard-library
pip install git+https://github.com/hellebore74/ceci
conda deactivate
conda activate firecrown_clp
cd ${CONDA_PREFIX}
source ${CONDA_PREFIX}/bin/cosmosis-configure
cosmosis-build-standard-library main
```
Now you will go back to the CLPipeline directory and run
```
conda env update -f txpipe_enviroment.yml
conda activate txpipe_clp
pip install git+https://github.com/hellebore74/ceci
```
To activate one or the other enviroment, run:
```
conda activate firecrown_cpl
```
or
```
conda activate txpipe_cpl
```

To build the package so it can be imported into a python file, run
```
python -m build
```

