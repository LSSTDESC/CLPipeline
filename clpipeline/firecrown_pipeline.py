#!/usr/bin/env python
#File dedicated to impement the Firecrown pipeline stage into ceci
from ceci_types import (
    SACCFile,
    YamlFile,
)
from ceci import PipelineStage
import sys
import firecrown

class FirecrownPipeline(PipelineStage):
    """
    Firecrown Pipeline stage.
    """
    name = "CLPFirecrown"

    inputs = [
        ("clusters_sacc_file", SACCFile),  # For firecrown Likelihood
        ("tracer_metadata_yml", YamlFile),  # For metadata
    ]

    outputs = [
        ("test", SACCFile),
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
        with self.open_input("test_metadata_yml", wrapper=True) as f:
            meta = f.content
        # check the units are what we are expecting
        assert meta["area_unit"] == "deg^2"
        assert meta["density_unit"] == "arcmin^{-2}"
        self.filter_yaml_sections("test_metadata_yml", "firecrown_metadata_yml", {"Firecrown": None})
        # Run firecrown
        # Here see how to generate the likelihood file with the counts example
        # Save if it is not automatically by firecrown of if we need to save something about this run
    
    def filter_yaml_sections(input_file, output_file, section_keys_to_extract):
        """
        Reads a YAML file, extracts specified parameters from defined sections, and writes them to a new YAML file.
        If no parameters are specified for a section, all parameters from that section will be extracted.

        Parameters:
        - input_file (str): Path to the input YAML file.
        - output_file (str): Path to the output YAML file where filtered parameters will be saved.
        - section_keys_to_extract (dict): Dictionary where keys are section names (e.g., "TXPipe")
          and values are lists of parameters to extract from those sections. If a section's value is an empty list,
          all parameters from that section will be extracted.

        Returns:
        - str: Path to the filtered YAML file if successful, or None if an error occurred.
        """
        try:
            # Read the input YAML file
            with open(input_file, 'r') as file:
                data = yaml.safe_load(file)
            
            # Filter the sections and parameters
            filtered_data = {}
            for section, keys in section_keys_to_extract.items():
                if section in data:
                    if not keys:  # Extract all parameters for the section if keys are empty
                        filtered_data[section] = data[section]
                    else:  # Extract only the specified parameters
                        filtered_data[section] = {key: data[section][key] for key in keys if key in data[section]}
            
            # Write the filtered data to a new YAML file
            with open(output_file, 'w') as file:
                yaml.dump(filtered_data, file, default_flow_style=False)
            
            print(f"Filtered YAML file created: {output_file}")
            return output_file
        
        except FileNotFoundError:
            print(f"Error: The file '{input_file}' was not found.")
            return None
        except yaml.YAMLError as e:
            print(f"Error: Problem reading or writing YAML file - {e}")
            return None
        except Exception as e:
            print(f"Unexpected error: {e}")
            return None

