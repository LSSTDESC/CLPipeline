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
        "firecrown_flag": False,
        "replace_tjpcov_cov": True,
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
        config_dict['sacc_file'] = sacc_file
        combined_config = {'tjpcov': config_dict}
        combined_config.update(config_dict)
        cc = CovarianceCalculator(combined_config)
        cov_terms     = cc.get_covariance_terms()
        sacc_with_cov = cc.create_sacc_cov(output=filename, save_terms=True, overwrite=True)
        print('Time: ', (time.time()-st), ' sec')
        if only_counts == False and has_covariance == True:
            new_sacc = self.extract_data_covariance(sacc_file, tjpcov_out_sacc)
        if config_dict["replace_tjpcov_cov"]:
            print("Replacing Counts TJPCov cov for Crow cov. SSC + Counts")
            self.replace_crow_counts(config_dict)

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
        import numpy as np
        if not hasattr(np, 'bool'):
            np.bool = bool  # add alias if missing
        # Load the input SACC file
        sacc_data_cov = sacc.Sacc.load_fits(input_sacc_file)
        sacc_final = sacc.Sacc.load_fits(output_sacc_file)
        data_types_sacc = [d_type for d_type in sacc_data_cov.get_data_types() if d_type != sacc.standard_types.cluster_counts]
        for d_type in data_types_sacc:
            ix1 = sacc_data_cov.indices(data_type=d_type)
            sacc_final.covariance.covmat[ix1,ix1] = sacc_data_cov.covariance.covmat[ix1,ix1]
        sacc_final.save_fits(output_sacc_file, overwrite=True)
        return sacc_final

    def replace_crow_counts(self, config_dict):
        import sacc
        import numpy as np
        import pyccl as ccl
        from crow import ClusterAbundance
        from crow.recipes.binned_grid import GridBinnedClusterRecipe
        from crow import completeness_models, mass_proxy, purity_models, kernel
        #This function should not exist as it should be implemented in TJPCov
        #This is temporary and so most of the options and configurations are fixed
        cosmo_params = config_dict["parameters"]
        cosmo = ccl.Cosmology(
            Omega_c=cosmo_params["Omega_c"],
            Omega_b=cosmo_params["Omega_b"],
            h=cosmo_params["h"],
            n_s=cosmo_params["n_s"],
            sigma8=cosmo_params["sigma8"],
            w0=cosmo_params["w0"],
            wa=cosmo_params["wa"],
            transfer_function=cosmo_params["transfer_function"]
        )
        mor_params = config_dict["mor_parameters"]
        hmf = ccl.halos.MassFuncDespali16(mass_def="200c")
        mass_richness_unb = mass_proxy.MurataUnbinned(pivot_log_mass=mor_params["m_pivot"], pivot_redshift=mor_params["z_pivot"])
        mass_richness_unb.parameters["mu0"]    = mor_params["mu_p0"]
        mass_richness_unb.parameters["mu1"]    = mor_params["mu_p1"]
        mass_richness_unb.parameters["mu2"]    = mor_params["mu_p2"]
        mass_richness_unb.parameters["sigma0"] = mor_params["sigma_p0"]
        mass_richness_unb.parameters["sigma1"] = mor_params["sigma_p1"]
        mass_richness_unb.parameters["sigma2"] = mor_params["sigma_p2"]

        mass_grid_size     = 80
        redshift_grid_size = 40
        proxy_grid_size    = 40
        mass_interval      = (np.log10(float(mor_params["min_halo_mass"])),np.log10(float(mor_params["max_halo_mass"])))
        cl_abundance          = ClusterAbundance(cosmo, hmf)
        purity_aguena         = purity_models.PurityAguena16()
        completeness_aguena   = completeness_models.CompletenessAguena16()
        redshift_distribution = kernel.SpectroscopicRedshift()
        recipe_grid_abundance = GridBinnedClusterRecipe(
            mass_interval=mass_interval,
            cluster_theory=cl_abundance,
            redshift_distribution=redshift_distribution,
            mass_distribution=mass_richness_unb,
            proxy_grid_size=proxy_grid_size,
            redshift_grid_size=redshift_grid_size,
            mass_grid_size=mass_grid_size,
            purity=purity_aguena,
            completeness=completeness_aguena
        )
        recipe_grid_abundance.setup()
        sacc_tjpcov_ssc = sacc.Sacc.load_fits(f"{config_dict['outdir']}/clusters_sacc_file_cov_SSC.sacc")
        sacc_tjpcov_counts = sacc.Sacc.load_fits(f"{config_dict['outdir']}/clusters_sacc_file_cov_gauss.sacc")
        sacc_tjpcov_full = sacc.Sacc.load_fits(f"{config_dict['outdir']}/clusters_sacc_file_cov.sacc")

        ssc_cov   = sacc_tjpcov_ssc.covariance.covmat.copy()
        counts_cov = sacc_tjpcov_counts.covariance.covmat.copy()
        full_cov  = sacc_tjpcov_full.covariance.covmat.copy()

        data_type = sacc.standard_types.cluster_counts
        data_points = sacc_tjpcov_full.get_data_points(data_type=data_type)
        theory_counts = {}

        for d_point in data_points:
            trs = d_point.tracers
            point_idx = sacc_tjpcov_full.indices(data_type=data_type, tracers=trs)
            tr_objs = [sacc_tjpcov_full.get_tracer(tr) for tr in trs]
            area   = tr_objs[0].sky_area
            rich_l = tr_objs[1].lower
            rich_u = tr_objs[1].upper
            z_l    = tr_objs[2].lower
            z_u    = tr_objs[2].upper
            k = point_idx[0]
            zb = [z_l, z_u]
            pb = [rich_l, rich_u]
            theory_counts[k] = recipe_grid_abundance.evaluate_theory_prediction_counts(
                np.array(zb), np.array(pb), area
            )

        for i in theory_counts:
            tjpcov_counts_i = counts_cov[i,i]
            ssc_term_i      = ssc_cov[i,i]
            old_cov_ii = full_cov[i,i]            
            full_cov[i,i]   = theory_counts[i] + ssc_term_i * theory_counts[i]**2 / (tjpcov_counts_i**2)
            print(f"Replaced cov points at {i,i}. From {old_cov_ii} to {full_cov[i,i]}")
            for j in theory_counts:
                if j <= i:
                    continue
                old_cov_ij      = full_cov[i,j]
                tjpcov_counts_j = counts_cov[j,j] 
                ssc_term_ij     = ssc_cov[i,j]
                val = ssc_term_ij * theory_counts[i] * theory_counts[j] / (tjpcov_counts_i * tjpcov_counts_j)
                full_cov[i,j] = val
                full_cov[j,i] = val
                print(f"Replaced cov points at {i,j}. From {old_cov_ij} to {full_cov[i,j]}")
        sacc_tjpcov_full.covariance = sacc.covariance.FullCovariance(full_cov)
        sacc_tjpcov_full.save_fits(f"{config_dict['outdir']}/clusters_sacc_file_cov.sacc", overwrite=True)
        




