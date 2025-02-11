# CLPipeline
Repository devoted to the Cluster working group from the DESC-LSST collaboration

To create both Firecrown and TXPipe conda enviroments, run: 
```
conda env update -f firecrown_enviroment.yml
conda env update -f txpipe_enviroment.yml
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

