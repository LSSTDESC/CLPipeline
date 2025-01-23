
# ceci - chain TXpipe, FireCrown & TJPcov computation - _LAPP 2025_

## Goal
chain several pipelines corresponding to different code packages that require different conda environment 
    ( for example : TXpipe, FireCrown, TPJcov, ... )

## Idea 
create a unique ceci pipeline file by concatenating the pipeline files corresponding to each package
- use the yaml multiple document feature  
- adapt ceci in order to be able to launch one pipeline at a time

and create a bash file that launches successively the different ceci pipelines

## ceci version used as basis for this development
```
commit 53f6d98387c4e589e1fb02647d1484bb60a21ead (HEAD -> master, origin/master, origin/HEAD)
Merge: cef8c11 1796495
Author: joezuntz <joezuntz@googlemail.com>
Date:   Sat Sep 21 07:29:11 2024 +0100

    Merge pull request #114 from LSSTDESC/resume-refuse-mode
    
    Add more options to the "resume" setting
```

### Global ceci yaml file  

The yaml file format follows the definition rules of a yaml multiple documents file :
- the file is a concatenation of the ceci yaml pipeline files seprated by a "---" substring
- the file starts and ends with a "---" substring
- in order to identify each section, a new parameter named id is added in each section

( see CL_test_concat.yml  which is a concatenation of tests/test.yml and tests/test_namespace.yml)

For example :

```
---
id: TXpipe
copy here the content of the txpipe yaml pipeline file
---
id: FireCrown
copy here the content of the FireCrown ceci pipeline file
---
id: TJPcov
copy here the content of the TJPCov ceci pipeline file
---
```

ceci was modified to launch each step separately by adding a yamlId paramater as an option.
- ceci global_pipeline.yaml --yamlId TXpipe    ==> launch the ceci pipeline for the pipeline defined in the "id: TXpipe" section
- ceci global_pipeline.yaml --yamlId FireCrown    ==> launch the ceci pipeline for the pipeline defined in the "id: FireCrown" section
- ceci global_pipeline.yaml --yamlId TJPCov    ==> launch the ceci pipeline for the pipeline defined in the "id: TJPCov" section

==> each group can develop, test and debug his package in his own conda environment without interfering with the other group

### Bash script

Example of bash script that chain the TXpipe, FireCrown and TJP cov codes. 
( One could also chain the jobs automatically by identifyind the different id sections) 

```
#!/bin/bash

cd my_directory_txpipe
source ./conda/activate
ceci global_pipeline.yaml --yamlId TXpipe
conda deactivate
source CL_clean_conda_env.sh

cd my_directory_firecrown
source ./conda/activate
ceci global_pipeline.yaml --yamlId FireCrown
conda deactivate
source CL_clean_conda_env.sh

cd my_directory_tjpcov
source ./conda/activate
ceci global_pipeline.yaml --yamlId TJPCov
conda deactivate
source CL_clean_conda_env.sh
```

### local install and setup  (Ubuntu 22.04)
```
python3 -m venv ceci_venv
cd ceci_venv
source ./bin/activate
pip install setuptools==61.1.0
pip install setuptools_scm
pip install pyyaml
pip install psutil

python3 setup.py build; python3 setup.py install
   
ceci tests_CL/CL_test_concat.yml --yamlId example1
ceci tests_CL/CL_test_concat.yml --yamlId example2
```

