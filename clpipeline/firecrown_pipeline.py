#!/usr/bin/env python
#File dedicated to impement the Firecrown pipeline stage into ceci
from .ceci_types import (
    SACCFile,
    YamlFile,
    PythonFile,
    CosmosisFile,
)
from ceci import PipelineStage
import sys
import os
import shutil
import re
class FirecrownPipeline(PipelineStage):
    """
    Firecrown Pipeline stage.
    """
    name = "FirecrownPipeline"

    inputs = [
        ("clusters_sacc_file", SACCFile),  # For firecrown Likelihood
    #    ("tracer_metadata_yml", YamlFile),  # For metadata
    ]

    outputs = [
        ("cluster_counts_mean_mass_redshift_richness", CosmosisFile),
        ("cluster_redshift_richness", PythonFile),
        ("cluster_richness_values", CosmosisFile),
    ]

    config_options = {
        "txpipe_flag": False,
        "firecrown_flag": True
    }

    def run(self):
        """
        Run the analysis for this stage.

         - Load global config file
         - Choose the right recipe based on the file
         - Output firecrown likelihood python file
        """
        import pyccl
        import firecrown
        import sacc
        ## Open the yaml configuration file
        my_config = self.config
        #print("Here is my configuration :", my_config)
        #print(self.outputs)
        #print(self.__dict__)
        #print(self.__dict__['_configs'])
        #methods = [func for func in dir(self) if callable(getattr(self, func)) and not func.startswith("__")]
        #print("Methods in class:", methods)
        ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
        FIRECROWN_INPUTS = ROOT_DIR.replace('clpipeline', 'firecrown_inputs')
        print(self.get_input("clusters_sacc_file"))
        self.cosmosis_files(FIRECROWN_INPUTS)
    def cosmosis_files(self, firecrown_inputs):
        new_sacc_path = self.get_input("clusters_sacc_file")
        input_dir = firecrown_inputs
        output_files = [self.get_output(out[0], final_name=True) for out in self.outputs_()]
        output_dir = os.path.dirname(output_files[0])
        files = [
        "cluster_counts_mean_mass_redshift_richness.ini",
        "cluster_redshift_richness.py",
        "cluster_richness_values.ini"
        ]
        os.makedirs(output_dir, exist_ok=True)
        for file in files:
            src = os.path.join(input_dir, file)
            dst = os.path.join(output_dir, file)
            if os.path.exists(src):
                shutil.copy(src, dst)
                print(f"Copied {file} to {output_dir}")
            else:
                print(f"Warning: {file} not found in {input_dir}")
        py_file_path = os.path.join(output_dir, "cluster_redshift_richness.py")

        if os.path.exists(py_file_path):
            with open(py_file_path, "r") as file:
                content = file.read()
            
            # Search for a string containing '.sacc' and replace it
            match = re.search(r'[\w/.\-]+\.sacc', content)

            if match:
                old_string = match.group()  # Extracts the matched full filename
                new_string = os.path.basename(self.get_input('clusters_sacc_file'))  # Replace this with the actual new filename

                modified_content = content.replace(old_string, new_string)

                with open(py_file_path, "w") as file:
                    file.write(modified_content)

            print(f"Modified {py_file_path}: replaced '{old_string}' with '{new_string}'")

        else:
            print(f"Error: {py_file_path} not found!")
