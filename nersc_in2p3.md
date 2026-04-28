# Shared Conda Environments for Cluster Working Group

This document describes how to create and manage **shared Conda environments** for the cluster working group on both **NERSC (Perlmutter)** and **IN2P3** systems.

The environments are installed in shared project directories and are intended for reuse across users.

---

## General Notes

- Always set `CONDA_PKGS_DIRS` to a **shared package cache** to avoid duplication.
- Use `--prefix` installs (not named environments) so environments live in shared paths.
- After creating an environment, you may need to:
  - Set environment variables
  - Re-activate the environment
  - Build external dependencies (e.g. CosmoSIS standard library)
- For MPI-based workflows (e.g. TXPipe), system MPI must be handled carefully.

---

# Firecrown Environments

## NERSC (Perlmutter)

### Standard Environment

```bash
export CONDA_PKGS_DIRS=/global/cfs/projectdirs/lsst/groups/CL/cl_pipeline_project/conda_envs/pkgs/firecrown_clp

conda env create \
  --prefix=/global/cfs/projectdirs/lsst/groups/CL/cl_pipeline_project/conda_envs/firecrown_clp \
  --file firecrown_environment.yml

conda activate /global/cfs/projectdirs/lsst/groups/CL/cl_pipeline_project/conda_envs/firecrown_clp

conda env config vars set CSL_DIR=${CONDA_PREFIX}/cosmosis-standard-library

conda deactivate
conda activate /global/cfs/projectdirs/lsst/groups/CL/cl_pipeline_project/conda_envs/firecrown_clp

cd ${CONDA_PREFIX}
source ${CONDA_PREFIX}/bin/cosmosis-configure
cosmosis-build-standard-library main
```

### Developer Environment (for branch work)
Use this when working with non-released versions of Firecrown.
```bash
conda env create \
  --prefix=/global/cfs/projectdirs/lsst/groups/CL/cl_pipeline_project/conda_envs/firecrown_developer_clp \
  --file firecrown_environment.yml

conda activate /global/cfs/projectdirs/lsst/groups/CL/cl_pipeline_project/conda_envs/firecrown_developer_clp

conda env config vars set CSL_DIR=${CONDA_PREFIX}/cosmosis-standard-library

conda deactivate
conda activate /global/cfs/projectdirs/lsst/groups/CL/cl_pipeline_project/conda_envs/firecrown_developer_clp

cd ${CONDA_PREFIX}
source ${CONDA_PREFIX}/bin/cosmosis-configure
cosmosis-build-standard-library main

# Install Firecrown from source
cd /global/cfs/projectdirs/lsst/groups/CL/cl_pipeline_project/
git clone https://github.com/LSSTDESC/firecrown.git
cd firecrown
pip install . --no-deps
```

## IN2P3

The procedure is identical to NERSC, but paths differ.

### Shared environment

```bash
export CONDA_PKGS_DIRS=/sps/lsst/groups/clusters/cl_pipeline_project/conda_envs/pkgs/firecrown_clp

conda env create \
  --prefix=/sps/lsst/groups/clusters/cl_pipeline_project/conda_envs/firecrown_clp \
  --file firecrown_environment.yml

conda activate /sps/lsst/groups/clusters/cl_pipeline_project/conda_envs/firecrown_clp

conda env config vars set CSL_DIR=${CONDA_PREFIX}/cosmosis-standard-library

conda deactivate
conda activate /sps/lsst/groups/clusters/cl_pipeline_project/conda_envs/firecrown_clp

cd ${CONDA_PREFIX}
source ${CONDA_PREFIX}/bin/cosmosis-configure
cosmosis-build-standard-library main
```

### Developer Environment

```bash
conda env create \
  --prefix=/sps/lsst/groups/clusters/cl_pipeline_project/conda_envs/firecrown_developer_clp \
  --file firecrown_environment.yml

conda activate /sps/lsst/groups/clusters/cl_pipeline_project/conda_envs/firecrown_developer_clp

conda env config vars set CSL_DIR=${CONDA_PREFIX}/cosmosis-standard-library

conda deactivate
conda activate /sps/lsst/groups/clusters/cl_pipeline_project/conda_envs/firecrown_developer_clp

cd ${CONDA_PREFIX}
source ${CONDA_PREFIX}/bin/cosmosis-configure
cosmosis-build-standard-library main

cd /sps/lsst/groups/clusters/cl_pipeline_project/
git clone https://github.com/LSSTDESC/firecrown.git
cd firecrown
pip install . --no-deps
```

## TXPipe Environments

TXPipe requires special handling of MPI dependencies, especially on Perlmutter (NERSC).

### NERSC (Perlmutter)
#### Installation

```bash
module load python
module load conda
export CONDA_PKGS_DIRS=/global/cfs/projectdirs/lsst/groups/CL/cl_pipeline_project/conda_envs/pkgs/txpipe_clp

module load mpich/4.3.0

export MPI4PY_RC_RECV_MPROBE='False'
export HDF5_USE_FILE_LOCKING=FALSE

conda env create \
  --prefix=/global/cfs/projectdirs/lsst/groups/CL/cl_pipeline_project/conda_envs/txpipe_clp \
  --file txpipe_environment_perlmutter.yml
```

#### Fix MPI Installation

```bash
conda activate /global/cfs/projectdirs/lsst/groups/CL/cl_pipeline_project/conda_envs/txpipe_clp
conda remove --force mpi4py libfabric libfabric1

MPI4PY_BUILD_MPIABI=1 MPICC="mpicc -shared" pip install --no-cache-dir --no-binary=mpi4py mpi4py
```

#### Activation Script Setup

```bash
mkdir -p /global/cfs/projectdirs/lsst/groups/CL/cl_pipeline_project/conda_envs/txpipe_clp/etc/conda/activate.d

cat > /global/cfs/projectdirs/lsst/groups/CL/cl_pipeline_project/conda_envs/txpipe_clp/etc/conda/activate.d/txpipe_clp.sh << 'EOF'
module load cray-mpich
export MPI4PY_RC_RECV_MPROBE='False'
export HDF5_USE_FILE_LOCKING=FALSE
export LD_LIBRARY_PATH=${MPICH_DIR}/lib-abi-mpich:${LD_LIBRARY_PATH}
export MPICH_GPU_SUPPORT_ENABLED=0
EOF
```

### IN2P3

```bash
export CONDA_PKGS_DIRS=/sps/lsst/groups/clusters/cl_pipeline_project/conda_envs/pkgs/txpipe_clp

conda env create \
  --prefix=/sps/lsst/groups/clusters/cl_pipeline_project/conda_envs/txpipe_clp \
  --file txpipe_environment.yml
```

## Summary

- Use shared directories (/global/cfs/... or /sps/...) for all environments.
- Always configure CONDA_PKGS_DIRS.
- Firecrown requires post-install CosmoSIS setup.
- Developer workflows require manual pip install from source.
- TXPipe on Perlmutter requires manual MPI handling and rebuild of mpi4py.