
import os
import sys
import shutil
import yaml

import ruamel.yaml
yaml_ruamel = ruamel.yaml.YAML()
yaml_ruamel.indent(mapping=2, sequence=4, offset=2)

from yaml_toolbox import *


def set_max_process_defined_in_stages(yaml_filename, pattern, max_process):

    data = get_document_from_yaml_file(yaml_filename, pattern)
    print(data)
    print("max process ",max_process)

    if not "stages" in data: return

    bUpdate = False
    for d in data["stages"]:
        print(d)
        if "nprocess" in d and d["nprocess"]>max_process: 
            bUpdate = True
            d["nprocess"]=max_process
            print("UPDATE : ",d)

    if not bUpdate: return

    #update yaml file
    yaml_ruamel.dump(data,open("file_tmp.yml", 'w'))

    update_yaml_file_document(yaml_filename, "file_tmp.yml", pattern[0]) 

    
def create_output_and_log_dirs(filename):
    """ Find the ouput_dir and log_dir parameter defined in global yaml file
        and create corresponding directories """

    print("OUTPUT AND LOG DIRS : ",filename)
    dirList=[]
    
    index=0
    bNextIndex=True
    while bNextIndex:
        data, raw_test = read_yaml_file_general(filename, index)
        if data==None:
            bNextIndex=False
        else:
            vList = get_values_recursively(data, "output_dir")
            dirList=dirList+vList
            vList = get_values_recursively(data, "log_dir")
            dirList=dirList+vList
            index+=1

    print(dirList)
    for dirname in dirList:
        if os.path.isdir(dirname): continue
        print("---> create directory : ",dirname)
        os.makedirs(dirname)
        
    return
    
    
    
def create_setup_variable_file(filename,filename_setup):
    """ Create setup files (CONDA_DIR, LOCAL_DIR, ...) for txpipe and tjpcov_firecronwn jobs in order
          to be able to launch the jobs locally """
    
    filename_setup_init=filename_setup
    pipe_config, raw_text = read_yaml_file_general(filename)
    varList=[x.strip() for x in pipe_config["setup"]["env_variables_setup"].split(" ") if x!=""]
    
    # Create environment variables for the txpipe pipeline
    text=[]
    reset_environment_parameter(pipe_config)
    setup_environment_parameter(pipe_config, "pipeline", True)
    setup_environment_parameter(pipe_config, "survey", True)
    setup_environment_parameter(pipe_config, "setup", True)
    setup_environment_parameter(pipe_config, "txpipe", True)
    config_text_init = os.path.expandvars(raw_text)
    pipe_config_expand = yaml_ruamel.load(config_text_init)

    for v0 in varList:
        v=v0.upper()
        if v in os.environ: text.append(f'export {v}="{os.environ[v]}"\n')

    filename_output=pipe_config_expand["txpipe"]["setup_file"]
    f=open(filename_output,"w")
    f.writelines(text)
    f.close()
    expand_variable_yaml_file(filename_output,None,pipe_config["setup"]["env_variables"])
    
    # Create environment variables for the tjpcov/firecrown pipeline    
    text=[]
    reset_environment_parameter(pipe_config)
    setup_environment_parameter(pipe_config, "pipeline", True)
    setup_environment_parameter(pipe_config, "survey", True)
    setup_environment_parameter(pipe_config, "setup", True)
    setup_environment_parameter(pipe_config, "tjpcov_firecrown", True)
    config_text_init = os.path.expandvars(raw_text)
    pipe_config_expand = yaml_ruamel.load(config_text_init)

    for v0 in varList:
        v=v0.upper()
        if v in os.environ: text.append(f'export {v}="{os.environ[v]}"\n')

    filename_output=pipe_config_expand["tjpcov_firecrown"]["setup_file"]
    f=open(filename_output,"w")
    f.writelines(text)
    f.close()    
    expand_variable_yaml_file(filename_output,None,pipe_config["setup"]["env_variables"])

    return

def read_and_decode_general_pipeline(filename,output_filename):
    """ Read the pipeline yaml file and expand all the environement variables 
        Save the result in the pipeline directory
    """

    pipe_config, raw_text = read_yaml_file_general(filename)
    
    # Create environment variables for the pipeline
    setup_environment_parameter(pipe_config, "pipeline", True)
    setup_environment_parameter(pipe_config, "survey", True)
    setup_environment_parameter(pipe_config, "txpipe", True)
    config_text_init = os.path.expandvars(raw_text)
    pipe_config_expand = yaml_ruamel.load(config_text_init)

    setup_environment_parameter(pipe_config, "tjpcov_firecrown", True)
    config_text_init = os.path.expandvars(raw_text)
    pipe_config_expand2 = yaml_ruamel.load(config_text_init)

    pipe_config_expand["tjpcov_firecrown"]=pipe_config_expand2["tjpcov_firecrown"].copy()

    #update yaml file
    yaml_ruamel.dump(pipe_config_expand,open(output_filename, 'w'))
    
    return


def createPipelineSetup(filename):
    """ Create the global pipeline yaml files  (TXpipe, TJPCov and FireCrown)
        - create a directory named ${LOCAL_DIR}/pipeline_id
        - copy the yaml config and pipeline files (TxPipe and CLPipeline ) in the directory
        - configure all the files by replacing environement parameters by their values
        - concatenate CLPipeline and TX pipe pipeline yaml files 

        all the files needed to launch the CLPipeline are stored in the directory with
          fully defined pathes for all the references to output and log dirs, data files, etc...
          ==> the CLPipeline can be launched from any filesystem directory 
    """

    pipe_config, raw_text = read_yaml_file_general(filename)
    
    # Create environment variables for the pipeline
    setup_environment_parameter(pipe_config, "pipeline", True)

    # Create directory based on pipeline Id and save a copy of the current clpipeline yml file
    pipeDir = os.environ["LOCAL_DIR"]+"/"+pipe_config["pipeline"]["pipeline_id"]
    print(f"Pipeline directory : {pipeDir}")
    if not os.path.isdir(pipeDir): os.makedirs(pipeDir)

    final_global_pipeline=pipeDir+"/clpipeline.yml"
    read_and_decode_general_pipeline(filename,final_global_pipeline)

    # ---------------------------------------------------------
    # Create TxPipe yaml file
    # ---------------------------------------------------------

    # Set the environement variables as defined in yaml file
    setup_environment_parameter(pipe_config, "txpipe", True)
    setup_environment_parameter(pipe_config, "survey", True)

    # Read the clpipeline yaml file
    config_text_init = os.path.expandvars(raw_text)
    pipe_config_env = yaml.safe_load(config_text_init)

    # Merge txpipe yaml and survey data files
    #   copy the txpipe and survey yaml files and merge them (inputs key)
    txpipe_tmp_yaml=pipeDir+"/txpipe_tmp.yml"
    print("Temporary txpipe yaml file : ", txpipe_tmp_yaml)
    merge_yaml_files(pipe_config_env["txpipe"]["pipeline_yaml"],  
                        pipe_config_env["survey"]["survey_data_files"],     
                        txpipe_tmp_yaml)    
    
    # Finalize the txpipe yaml file  (replace env variables by real names)
    #     a txpipe_standalone.ymal is stored in the pipeline directory
    txpipe_final_yaml=pipeDir+"/txpipe_standalone.yml"
    expand_variable_yaml_file(txpipe_tmp_yaml, txpipe_final_yaml,pipe_config["setup"]["env_variables"])
    yaml_set_value(final_global_pipeline,"txpipe:pipeline_yaml",txpipe_final_yaml)
    
    # Copy the txpipe config yaml file to pipeline directory
    configYamlFile = yaml_get_value(txpipe_final_yaml, "config")
    local_configYamlFile = pipeDir+"/"+configYamlFile.split("/")[-1]
    shutil.copy(configYamlFile,local_configYamlFile)
    # Modify the config key in the txpipe yaml in order to point to the pipedir config file
    yaml_set_value(txpipe_final_yaml,"config",local_configYamlFile)
    yaml_set_value(final_global_pipeline,"txpipe:config_yaml",local_configYamlFile)
    
    # Finalize the config yaml file (replace env variables by real names)
    expand_variable_yaml_file(local_configYamlFile, None, pipe_config["setup"]["env_variables"])
    

    # ---------------------------------------------------------
    # Create TJPCov and FireCrown yaml file
    # ---------------------------------------------------------

    # Set the environement variables as defined in clpipeline yaml file
    reset_environment_parameter(pipe_config)
    setup_environment_parameter(pipe_config, "pipeline", True)
    setup_environment_parameter(pipe_config, "tjpcov_firecrown", True)
    setup_environment_parameter(pipe_config, "survey", True)

    # Read the tjpcov_firecrown section from yaml file
    config_text_init = os.path.expandvars(raw_text)
    pipe_config_env = yaml.safe_load(config_text_init)

    # Copy the tjpcov_firecron pipeline yaml file to the pipeline directory
    pipelineYamlFile = pipe_config_env["tjpcov_firecrown"]["pipeline_yaml"]
    local_pipelineYamlFile = pipeDir+"/"+pipelineYamlFile.split("/")[-1]
    shutil.copy(pipelineYamlFile,local_pipelineYamlFile)

    # Finalize the pipeline yaml file (replace env variables by real names)
    expand_variable_yaml_file(local_pipelineYamlFile, None, pipe_config["setup"]["env_variables"])
    yaml_set_value(final_global_pipeline,"tjpcov_firecrown:pipeline_yaml",local_pipelineYamlFile)
    yaml_set_value(final_global_pipeline,"pipeline:CLpipeline_yaml",local_pipelineYamlFile)
    
    # Copy the config.yaml file to the pipeline directory
    #    ( taking into account that config files are defined in different sections of the yaml file )
    configYamlFile = yaml_get_value(local_pipelineYamlFile, "config")
    print(">>>>>>>> " ,configYamlFile)
    copiedYamlFiles=[]
    for nameConfig in configYamlFile:
        if nameConfig==None:
            copiedYamlFiles.append(None)
            continue
        local_configYamlFile = pipeDir+"/"+nameConfig.split("/")[-1]
        if local_configYamlFile in copiedYamlFiles:
            copiedYamlFiles.append(local_configYamlFile)
            continue
        # copy yaml file to pipeline directory
        shutil.copy(nameConfig,local_configYamlFile)
        # Finalize config yaml file (replace env variables by real names)
        expand_variable_yaml_file(local_configYamlFile, None, pipe_config["setup"]["env_variables"])

    # Update config yaml file names in pipeline yaml file
    for i,v in enumerate(copiedYamlFiles):
        if v==None: continue
        yaml_set_value(local_pipelineYamlFile,"config",v,i)

    yaml_set_value(final_global_pipeline,"tjpcov_firecrown:config_yaml",local_configYamlFile)

    # ---------------------------------------------------------
    # Update TxPipe document nested in concatenated yaml file
    # ---------------------------------------------------------
    update_yaml_file_document(local_pipelineYamlFile,txpipe_final_yaml,"id:TXPipe")

    # ---------------------------------------------------------
    # Create environement variable setup file
    # ---------------------------------------------------------
    local_setupFile = pipeDir+"/setup.sh"
    create_setup_variable_file(final_global_pipeline, local_setupFile)

    # ---------------------------------------------------------
    # Create output and log dirs
    # ---------------------------------------------------------
    create_output_and_log_dirs(local_pipelineYamlFile)

    


    
