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
        ("clusters_sacc_file_cov", SACCFile),
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
        import os

        # tjpcov packages
        from tjpcov.covariance_calculator import CovarianceCalculator
        from tjpcov.covariance_cluster_counts_ssc import ClusterCountsSSC

        # compute covariance terms from the covariance class (and save results in a .sacc file)
        st = time.time()
        tjpcov_out_sacc = self.get_output('clusters_sacc_file_cov', final_name=True) 
        config_dict = self.config.to_dict()
        outdir = os.path.dirname(tjpcov_out_sacc)
        filename = os.path.basename(tjpcov_out_sacc)
        config_dict = self.config.to_dict()
        config_dict['outdir'] = outdir
        combined_config = {'tjpcov': config_dict}
        combined_config.update(config_dict)
        cc = CovarianceCalculator(combined_config)
        print(cc.config)
        cc.config['tjpcov']['photo-z']['sigma_0'] = 0.05
        
        print(tjpcov_out_sacc)
        cov_terms     = cc.get_covariance_terms()
        sacc_with_cov = cc.create_sacc_cov(output=filename, save_terms=True)
        print('Time: ', (time.time()-st), ' sec')
