from .ceci_types import (
    SACCFile,
    YamlFile,
)
from ceci import PipelineStage
import sys


class TXPipePipeline(PipelineStage):
    """
    TXPipe Pipeline stage.
    """
    name = "TXPipePipeline"

    inputs = [
        ("clusters_sacc_file", SACCFile),  # For firecrown Likelihood
    #    ("tracer_metadata_yml", YamlFile),  # For metadata
    ]

    outputs = [
        ("test.sacc", SACCFile),
    ]

    config_options = {
        "txpipe_flag": True,
        "firecrown_flag": False
    }

    def run(self):
        """
        Run the analysis for this stage.

         - Load global config file
         - Choose the right recipe based on the file
         - Output firecrown likelihood python file
        """
        import numpy as np
        import matplotlib.pyplot as plt
        import sacc
        import sys
        import ceci
        import os
        import pickle as pkl
        sys.path.insert(0, '/sps/lsst/groups/clusters/cl_pipeline_project/TXPipe')
        import txpipe
        import yaml
        
        print(self.config)
        ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
        CONFIG_DIR = ROOT_DIR.replace('clpipeline', 'inputs_config')
        print(ROOT_DIR)
        pipeline_config = None
        if self.config['survey'] == 'cosmodc2_20deg2':
            pipeline_file = os.path.join(CONFIG_DIR, "cosmodc2/pipeline-20deg2-CL-in2p3.yml")
            flowchart_file = "CL_pipeline.png"
            pipeline_config = ceci.Pipeline.build_config(pipeline_file, flow_chart=flowchart_file, dry_run=False)
            print(pipeline_config)
            ceci.prepare_for_pipeline(pipeline_config)
            ceci.run_pipeline(pipeline_config)
            #with open(pipeline_file, "r") as file:
            #    pipeline_content = yaml.safe_load(file)
            #data = pkl.load(open(pipeline_content["output_dir"] + "/cluster_profiles.pkl", "rb"))
            #print(data)
    def convert_to_sacc(self):
        pass
