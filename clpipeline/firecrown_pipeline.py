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
import textwrap
import numpy as np
class FirecrownPipeline(PipelineStage):
    """
    Firecrown Pipeline stage.
    """
    name = "FirecrownPipeline"

    inputs = [
        ("clusters_sacc_file_cov", SACCFile),  # For firecrown Likelihood
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
        print(self.get_input("clusters_sacc_file_cov"))
        output_cosmosis_file = self.get_output('cluster_counts_mean_mass_redshift_richness', final_name=True)
        output_likelihood_file = self.get_output('cluster_redshift_richness', final_name=True)
        self.generate_python_file(my_config, output_likelihood_file)#self.cosmosis_files(FIRECROWN_INPUTS)
        self.generate_ini_file(my_config, output_cosmosis_file)
        print(my_config['cosmological_parameters'])
        self.generate_cosmosis_parameters_file(my_config, self.get_output('cluster_richness_values', final_name=True))
    def generate_python_file(self, yml_config, path_name):
        """
        Generates a Python file based on the configuration dictionary.

        Args:
            config (dict): Configuration dictionary.
            path_name (str): Path to save the generated Python file.
        """
        my_configs = self.config
        sacc_file_name = os.path.basename(self.get_input('clusters_sacc_file_cov'))
        hmf_dict = {
            'angulo12': 'ccl.halos.MassFuncAngulo12',
            'bocquet16': 'ccl.halos.MassFuncBocquet16',
            'bocquet20': 'ccl.halos.MassFuncBocquet20',
            'despali16': 'ccl.halos.MassFuncDespali16',
            'jenkins01': 'ccl.halos.MassFuncJenkins01',
            'press74': 'ccl.halos.MassFuncPress74',
            'sheth99': 'ccl.halos.MassFuncSheth99',
            'tinker08': 'ccl.halos.MassFuncTinker08',
            'tinker10': 'ccl.halos.MassFuncTinker10',
            'watson13': 'ccl.halos.MassFuncWatson13',
        }
        try:
            # Extract values from the configuration
            hmf_key = yml_config.get('hmf', 'bocquet16')  # Default to 'bocquet16' if not specified
            hmf = hmf_dict.get(hmf_key, 'ccl.halos.MassFuncBocquet16()')  # Default to MassFuncBocquet16 if not found
            min_mass = yml_config.get('min_mass', 13.0)
            max_mass = yml_config.get('max_mass', 16.0)
            min_z = yml_config.get('min_z', 0.2)
            max_z = yml_config.get('max_z', 0.8)
            pivot_mass = yml_config.get('pivot_mass', 14.3)
            pivot_z = yml_config.get('pivot_z', 0.6)
            survey_name = yml_config.get('survey_name', 'numcosmo_simulated_redshift_richness')
            sacc_path = sacc_file_name
            ln_pivot_mass = np.log(10**pivot_mass)
            use_mean_deltasigma = yml_config.get('use_mean_deltasigma', False)
            set_cluster_concentration = yml_config.get('set_concentration', False)
            # Open the file to be written
            with open(path_name, 'w') as f:
                f.write("import os\n")
                f.write("import pyccl as ccl\n")
                f.write("import sacc\n")
                f.write("from firecrown.likelihood.gaussian import ConstGaussian\n")
                f.write("from firecrown.likelihood.binned_cluster_number_counts import BinnedClusterNumberCounts\n")
                f.write("from firecrown.likelihood.likelihood import Likelihood, NamedParameters\n")
                f.write("from firecrown.modeling_tools import ModelingTools\n")
                f.write("from firecrown.models.cluster.abundance import ClusterAbundance\n")
                f.write("from firecrown.models.cluster.properties import ClusterProperty\n")
                f.write("from firecrown.models.cluster.recipes.murata_binned_spec_z import MurataBinnedSpecZRecipe\n\n")
                if use_mean_deltasigma:
                    f.write("from firecrown.models.cluster.recipes.murata_binned_spec_z_deltasigma import MurataBinnedSpecZDeltaSigmaRecipe\n")
                    f.write("from firecrown.models.cluster.deltasigma import ClusterDeltaSigma\n")
                    f.write("from firecrown.likelihood.binned_cluster_number_counts_deltasigma import BinnedClusterDeltaSigma\n")
                f.write("def get_cluster_abundance() -> ClusterAbundance:\n")
                f.write("    '''Creates and returns a ClusterAbundance object.''' \n")
                f.write(f"    hmf = {hmf}(mass_def='200c')  # Using {hmf_key} from the config\n")
                f.write(f"    min_mass, max_mass = {min_mass}, {max_mass}\n")
                f.write(f"    min_z, max_z = {min_z}, {max_z}\n")
                f.write("    cluster_abundance = ClusterAbundance((min_mass, max_mass), (min_z, max_z), hmf)\n\n")
                f.write("    return cluster_abundance\n\n")
                if use_mean_deltasigma:
                    f.write("def get_cluster_deltasigma() -> ClusterDeltaSigma:\n")
                    f.write("    '''Creates and returns a ClusterDeltaSigma object.'''\n")
                    f.write("    hmf = ccl.halos.MassFuncTinker08(mass_def='200c')\n")
                    f.write("    min_mass, max_mass = 13.0, 16.0\n")
                    f.write("    min_z, max_z = 0.2, 0.8\n")
                    f.write("    cluster_deltasigma = ClusterDeltaSigma(\n")
                    f.write(f"        (min_mass, max_mass), (min_z, max_z), hmf, {set_cluster_concentration}\n")
                    f.write("    )\n\n")
                    f.write("    return cluster_deltasigma\n\n")
                f.write("def build_likelihood(build_parameters: NamedParameters) -> tuple[Likelihood, ModelingTools]:\n")
                f.write("    '''Builds the likelihood for Firecrown.''' \n")
                f.write("    # Pull params for the likelihood from build_parameters\n")
                f.write("    average_on = ClusterProperty.NONE\n")
                f.write("    if build_parameters.get_bool('use_cluster_counts', True):\n")
                f.write("        average_on |= ClusterProperty.COUNTS\n")
                f.write("    if build_parameters.get_bool('use_mean_log_mass', True):\n")
                f.write("        average_on |= ClusterProperty.MASS\n")
                f.write("    if build_parameters.get_bool('use_mean_deltasigma', True):\n")
                f.write("        average_on |= ClusterProperty.DELTASIGMA\n\n")
                f.write(f"    recipe_counts = MurataBinnedSpecZRecipe()\n")
                f.write(f"    recipe_counts.mass_distribution.pivot_mass = {ln_pivot_mass}\n")
                f.write(f"    recipe_counts.mass_distribution.pivot_redshift = {pivot_z}\n")
                f.write(f"    recipe_counts.mass_distribution.log1p_pivot_redshift = {np.log1p(pivot_z)}\n")
                f.write(f"    survey_name = '{survey_name}'\n")
                if use_mean_deltasigma:
                    f.write(f"    recipe_delta_sigma = MurataBinnedSpecZDeltaSigmaRecipe()\n")
                    f.write(f"    recipe_delta_sigma.mass_distribution.pivot_mass = {ln_pivot_mass}\n")
                    f.write(f"    recipe_delta_sigma.mass_distribution.pivot_redshift = {pivot_z}\n")
                    f.write(f"    recipe_delta_sigma.mass_distribution.log1p_pivot_redshift = {np.log1p(pivot_z)}\n")
                    f.write("    likelihood = ConstGaussian(\n")
                    f.write("        [\n")
                    f.write("            BinnedClusterNumberCounts(\n")
                    f.write("                average_on, survey_name, recipe_counts\n")
                    f.write("            ),\n")
                    f.write("            BinnedClusterDeltaSigma(\n")
                    f.write("                average_on, survey_name, recipe_delta_sigma\n")
                    f.write("            ),\n")
                    f.write("        ]\n")
                else:
                    f.write("    likelihood = ConstGaussian(\n")
                    f.write("        [BinnedClusterNumberCounts(average_on, survey_name, recipe_counts)]\n")
                f.write("    )\n\n")
                f.write(f"    sacc_path = '{sacc_path}'\n")
                f.write("    sacc_data = sacc.Sacc.load_fits(sacc_path)\n")
                f.write("    likelihood.read(sacc_data)\n\n")

                f.write("    cluster_abundance = get_cluster_abundance()\n")
                if use_mean_deltasigma:
                    f.write("    cluster_deltasigma = get_cluster_deltasigma()\n")
                    f.write("    modeling_tools = ModelingTools(cluster_abundance=cluster_abundance, cluster_deltasigma=cluster_deltasigma)\n\n")
                else:
                    f.write("    modeling_tools = ModelingTools(cluster_abundance=cluster_abundance)\n\n")
                f.write("    return likelihood, modeling_tools\n")

            print(f"Python file generated at {path_name}")
            return True

        except Exception as e:
            print(f"Error generating file: {e}")
            return False

    def generate_ini_file(self, config, output_ini_path):
        """
        Generates an .ini file based on the configuration dictionary.

        Args:
            config (dict): Configuration dictionary containing the values for substitution.
            output_ini_path (str): Path where the generated .ini file will be saved.
        """
        import cosmosis
        import firecrown

        try:
            # Get the configuration values
            sampler = config.get('sampler', 'test')
            root = os.getcwd()  # Using current working directory for root
            out_filename = config.get('filename', 'output_rp/number_counts_samples.txt')
            
            use_cluster_counts = config.get('use_cluster_counts', True)
            use_mean_log_mass = config.get('use_mean_log_mass', True)
            
            # Emcee configuration
            emcee_walkers = config.get('emcee_walkers', 20)
            emcee_samples = config.get('emcee_samples', 4000)
            emcee_nsteps = config.get('emcee_nsteps', 10)

            FIRECROWN_DIR = os.path.dirname(firecrown.__file__)

            with open(output_ini_path, 'w') as f:
                f.write("[runtime]\n")
                f.write(f"sampler = {sampler}\n")
                f.write(f"root = {root}\n\n")

                f.write("[default]\n")
                f.write("fatal_errors = T\n\n")

                f.write("[output]\n")
                f.write(f"filename = {out_filename}\n")
                f.write("format = text\n")
                f.write("verbosity = 0\n\n")

                f.write("[pipeline]\n")
                f.write("modules = consistency camb firecrown_likelihood\n")
                f.write("values = cluster_richness_values.ini\n")
                f.write("likelihoods = firecrown\n")
                f.write("quiet = T\n")
                f.write("debug = T\n")
                f.write("timing = T\n\n")

                f.write("[consistency]\n")
                f.write("file = ${CSL_DIR}/utility/consistency/consistency_interface.py\n\n")

                f.write("[camb]\n")
                f.write("file = ${CSL_DIR}/boltzmann/camb/camb_interface.py\n\n")
                f.write("mode = all\n")
                f.write("lmax = 2500\n")
                f.write("feedback = 0\n")
                f.write("zmin = 0.0\n")
                f.write("zmax = 1.0\n")
                f.write("nz = 100\n")
                f.write("kmin = 1e-4\n")
                f.write("kmax = 50.0\n")
                f.write("nk = 1000\n\n")

                f.write("[firecrown_likelihood]\n")
                f.write(";; Fix this to use an environment variable to find the files.\n")
                f.write(";; Set FIRECROWN_DIR to the base of the firecrown installation (or build, if you haven't installed it)\n")
                f.write(f"file = {FIRECROWN_DIR}/connector/cosmosis/likelihood.py\n")
                f.write("likelihood_source = cluster_redshift_richness.py\n")
                f.write("sampling_parameters_sections = firecrown_number_counts\n")
                f.write(f"use_cluster_counts = {str(use_cluster_counts).upper()}\n")
                f.write(f"use_mean_log_mass = {str(use_mean_log_mass).upper()}\n\n")
                f.write("[test]\n")
                f.write("fatal_errors = T\n")
                f.write("save_dir = output_counts_mean_mass\n\n")

                f.write("[metropolis]\n")
                f.write("samples = 1000\n")
                f.write("nsteps = 1\n\n")

                f.write("[emcee]\n")
                f.write(f"walkers = {emcee_walkers}\n")
                f.write(f"samples = {emcee_samples}\n")
                f.write(f"nsteps = {emcee_nsteps}\n")

            print(f"INI file written to {output_ini_path}")
            print(f"INI file generated at {output_ini_path}")
            return True

        except Exception as e:
            print(f"Error generating INI file: {e}")
            return False

    def generate_cosmosis_parameters_file(self, config, output_ini_path):
        """
        Generates a .ini file based on the configuration dictionary.

        Args:
            config (dict): Configuration dictionary containing the values for substitution.
            output_ini_path (str): Path where the generated .ini file will be saved.
        """
        try:
            with open(output_ini_path, 'w') as f:
                f.write("; Parameters and data in CosmoSIS are organized into sections\n")
                f.write("; so we can easily see what they mean.\n")
                f.write("; There is only one section in this case, called cosmological_parameters\n")
                f.write("[cosmological_parameters]\n")
                f.write("; These are the only cosmological parameters being varied.\n")
                for param, value in config.get('cosmological_parameters', {}).items():
                    if value['sample']:
                        f.write(f"{param} = {value['values'][0]} {value['values'][1]} {value['values'][2]}\n")

                f.write("; The following parameters are set, but not varied.\n")
                for param, value in config.get('cosmological_parameters', {}).items():
                    if not value['sample']:
                        f.write(f"{param} = {value['values']}\n")
                
                f.write("[firecrown_number_counts]\n")
                f.write("; These are the firecrown likelihood parameters.\n")
                f.write("; These parameters are used to set the richness-mass\n")
                f.write("; proxy relation using the data from cluster number counts.\n")
                
                # Writing firecrown_number_counts parameters
                for param, value in config.get('firecrown_parameters', {}).items():
                    if value['sample']:
                        f.write(f"{param} = {value['values'][0]} {value['values'][1]} {value['values'][2]}\n")
                    else:
                        f.write(f"{param} = {value['values']}\n")
                
            print(f"INI file written to {output_ini_path}")
            return True
        
        except Exception as e:
            print(f"Error generating INI file: {e}")
            return False
