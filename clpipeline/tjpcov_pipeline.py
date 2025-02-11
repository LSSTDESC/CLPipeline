#!/usr/bin/env python
#File dedicated to impement the Firecrown pipeline stage into ceci
from .ceci_types import (
    SACCFile,
    YamlFile,
)
from ceci import PipelineStage
import sys


class TJPCovPipeline(PipelineStage):
    """
    TJPCov Pipeline stage.
    """
    name = "TJPCovPipeline"

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
        import pyccl as ccl
        import time

        # tjpcov packages
        from tjpcov.covariance_calculator import CovarianceCalculator
        from tjpcov.covariance_cluster_counts_ssc import ClusterCountsSSC

        # compute covariance terms from the covariance class (and save results in a .sacc file)
        st = time.time()
        config_dict = self.config.to_dict()
        combined_config = {'tjpcov': config_dict}
        combined_config.update(config_dict)
        cc = CovarianceCalculator(combined_config)
        print(cc.config)
        cc.config['tjpcov']['photo-z']['sigma_0'] = 0.05

        cov_terms     = cc.get_covariance_terms()
        sacc_with_cov = cc.create_sacc_cov(output="test_cov_new_05.sacc", save_terms=True)
        print('Time: ', (time.time()-st), ' sec')
        ## Open the yaml configuration file
        print(f"My config : {self.config}")
        for inp, _ in self.inputs:
            filename = self.get_input(inp)
            print(f"    TJPCov reading from {filename}")
            open(filename)

        for out, _ in self.outputs:
            filename = self.get_output(out)
            print(f"    shearMeasurementPipe writing to {filename}")
            open(filename, "w").write("shearMeasurementPipe was here \n")



