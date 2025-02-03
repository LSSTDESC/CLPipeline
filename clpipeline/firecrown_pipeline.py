#!/usr/bin/env python
#File dedicated to impement the Firecrown pipeline stage into ceci
from .ceci_types import (
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
    name = "FirecrownPipeline"

    inputs = [
        ("clusters_sacc_file", SACCFile),  # For firecrown Likelihood
    #    ("tracer_metadata_yml", YamlFile),  # For metadata
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
        my_config = self.config
        print("Here is my configuration :", my_config)
        # with self.open_input("test_metadata_yml", wrapper=True) as f:
        #     meta = f.content
        # # check the units are what we are expecting
        # assert meta["area_unit"] == "deg^2"
        # assert meta["density_unit"] == "arcmin^{-2}"
        # Run firecrown
        # Here see how to generate the likelihood file with the counts example
        # Save if it is not automatically by firecrown of if we need to save something about this run
    
