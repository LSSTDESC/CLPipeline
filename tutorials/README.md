# Nersc Jupyter Platform
Before running these tutorials in a jupyter notebook, one must install the jupyter kernel related to `firecrown_clp` and `txpipe_clp`. To do so, one may follow https://docs.nersc.gov/services/jupyter/how-to-guides/. However, we have already set these files and the user might just copy these existent files. To do, follow the commands:

```
cp -r /global/cfs/projectdirs/lsst/groups/CL/cl_pipeline_project/jupyter_kernels/firecrown_clp/     ${HOME}/.local/share/jupyter/kernels/firecrown_clp
cp -r /global/cfs/projectdirs/lsst/groups/CL/cl_pipeline_project/jupyter_kernels/txpipe_clp/ ${HOME}/.local/share/jupyter/kernels/txpipe_clp
```
With these files, one can check that the `Txpipe_clp` and `Firecrown_clp` kernels are available in the jupyter platform at https://jupyter.nersc.gov/.
