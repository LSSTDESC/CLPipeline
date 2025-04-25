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
         - Insert this configuration into the TJPCov configuration
         - Compute the theoretical covariance for counts
         - Keep old data drive covariance terms for other data types
        """
        import sacc
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
        sacc_file = self.get_input("clusters_sacc_file")
        # Load the SACC file
        sacc_obj = sacc.Sacc.load_fits(sacc_file)

        # Check if the data contains only cluster counts
        data_types = set(dp.data_type for dp in sacc_obj.data)
        only_counts = data_types == {sacc.standard_types.cluster_counts}

        # Check if covariance is present
        has_covariance = sacc_obj.covariance is not None
        # print(sacc_file)
        config_dict['sacc_file'] = sacc_file
        combined_config = {'tjpcov': config_dict}
        combined_config.update(config_dict)
        cc = CovarianceCalculator(combined_config)
        # print(cc.config)
        # print(tjpcov_out_sacc)
        cov_terms     = cc.get_covariance_terms()
        sacc_with_cov = cc.create_sacc_cov(output=filename, save_terms=True)
        print('Time: ', (time.time()-st), ' sec')
        if only_counts == False and has_covariance == True:
            new_sacc = self.extract_data_covariance(sacc_file, tjpcov_out_sacc)
        
    def extract_and_save_cluster_counts(self, input_sacc_file: str, output_sacc_file: str):
        """
        Reads a SACC file, extracts only the cluster counts data (without covariance),
        and saves it to a new SACC file.

        Args:
            input_sacc_file (str): Path to the input SACC file containing full data.
            output_sacc_file (str): Path where the new SACC file with only cluster counts will be saved.
        """
        import sacc
        # Load the input SACC file
        sacc_obj = sacc.Sacc.load_fits(input_sacc_file)

        # Create a new SACC object for the extracted data
        new_sacc = sacc.Sacc()

        # Copy relevant tracers to the new SACC object
        for tracer_name, tracer in sacc_obj.tracers.items():
            new_sacc.add_tracer_object(tracer)

        # Extract only cluster counts data points
        cluster_count_type = sacc.standard_types.cluster_counts
        cluster_counts_points = sacc_obj.get_data_points(cluster_count_type)

        for point in cluster_counts_points:
            new_sacc.add_data_point(cluster_count_type, point.tracers, point.value)

        # Save the new SACC object to the specified file (without covariance)
        new_sacc.to_canonical_order()
        new_sacc.save_fits(output_sacc_file, overwrite=True)
        return output_sacc_file
    
    def extract_data_covariance(self, input_sacc_file: str, output_sacc_file: str):
        """
        Reads a SACC file, extracts only the cluster counts data (without covariance),
        and saves it to a new SACC file.

        Args:
            input_sacc_file (str): Path to the input SACC file containing full data.
            output_sacc_file (str): Path where the new SACC file with only cluster counts will be saved.
        """
        import sacc
        # Load the input SACC file
        sacc_data_cov = sacc.Sacc.load_fits(input_sacc_file)
        sacc_final = sacc.Sacc.load_fits(output_sacc_file)
        data_types_sacc = [d_type for d_type in sacc_data_cov.get_data_types() if d_type != sacc.standard_types.cluster_counts]
        for d_type in data_types_sacc:
            ix1 = sacc_data_cov.indices(data_type=d_type)
            sacc_final.covariance.covmat[ix1,ix1] = sacc_data_cov.covariance.covmat[ix1,ix1]
        sacc_final.save_fits(output_sacc_file, overwrite=True)
        return sacc_final