import os
import pyccl as ccl
import sacc
import sys
sys.path.insert(0, "/sps/lsst/users/ebarroso/CLPipeline")
from firecrown.likelihood.gaussian import ConstGaussian
from firecrown.likelihood.binned_cluster_number_counts import BinnedClusterNumberCounts
from firecrown.likelihood.likelihood import Likelihood, NamedParameters
from firecrown.modeling_tools import ModelingTools
from firecrown.models.cluster.abundance import ClusterAbundance
from firecrown.models.cluster.properties import ClusterProperty
from clpipeline.firecrown_recipes.counts_cp import MurataBinnedSpecZSelectionRecipe

from clpipeline.firecrown_recipes.deltasigma_cp import MurataBinnedSpecZDeltaSigmaSelectionRecipe
from firecrown.models.cluster.deltasigma import ClusterDeltaSigma
from firecrown.likelihood.binned_cluster_number_counts_deltasigma import BinnedClusterDeltaSigma
def get_cluster_abundance() -> ClusterAbundance:
    '''Creates and returns a ClusterAbundance object.''' 
    hmf = ccl.halos.MassFuncDespali16(mass_def='200c')  # Using despali16 from the config
    min_mass, max_mass = 12.0, 15.5
    min_z, max_z = 0.2, 0.8
    cluster_abundance = ClusterAbundance((min_mass, max_mass), (min_z, max_z), hmf)

    return cluster_abundance

def get_cluster_deltasigma() -> ClusterDeltaSigma:
    '''Creates and returns a ClusterDeltaSigma object.'''
    hmf = ccl.halos.MassFuncTinker08(mass_def='200c')
    min_mass, max_mass = 13.0, 16.0
    min_z, max_z = 0.2, 0.8
    cluster_deltasigma = ClusterDeltaSigma(
        (min_mass, max_mass), (min_z, max_z), hmf, False
    )

    return cluster_deltasigma

def build_likelihood(build_parameters: NamedParameters) -> tuple[Likelihood, ModelingTools]:
    '''Builds the likelihood for Firecrown.''' 
    # Pull params for the likelihood from build_parameters
    average_on = ClusterProperty.NONE
    if build_parameters.get_bool('use_cluster_counts', True):
        average_on |= ClusterProperty.COUNTS
    if build_parameters.get_bool('use_mean_log_mass', True):
        average_on |= ClusterProperty.MASS
    if build_parameters.get_bool('use_mean_deltasigma', True):
        average_on |= ClusterProperty.DELTASIGMA

    recipe_counts = MurataBinnedSpecZSelectionRecipe()
    recipe_counts.mass_distribution.pivot_mass = 32.92696682981485
    recipe_counts.mass_distribution.pivot_redshift = 0.5
    recipe_counts.mass_distribution.log1p_pivot_redshift = 0.4054651081081644
    survey_name = 'cosmodc2-440deg2-CL'
    recipe_delta_sigma = MurataBinnedSpecZDeltaSigmaSelectionRecipe()
    recipe_delta_sigma.mass_distribution_unb.pivot_mass = 32.92696682981485
    recipe_delta_sigma.mass_distribution_unb.pivot_redshift = 0.5
    recipe_delta_sigma.mass_distribution_unb.log1p_pivot_redshift = 0.4054651081081644
    recipe_delta_sigma.mass_distribution.pivot_mass = 32.92696682981485
    recipe_delta_sigma.mass_distribution.pivot_redshift = 0.5
    recipe_delta_sigma.mass_distribution.log1p_pivot_redshift = 0.4054651081081644
    likelihood = ConstGaussian(
        [
            BinnedClusterNumberCounts(
                average_on, survey_name, recipe_counts
            ),
            BinnedClusterDeltaSigma(
                average_on, survey_name, recipe_delta_sigma
            ),
        ]
    )

    sacc_path = 'clusters_sacc_file_cov.sacc'
    sacc_data = sacc.Sacc.load_fits(sacc_path)
    likelihood.read(sacc_data)

    cluster_abundance = get_cluster_abundance()
    cluster_deltasigma = get_cluster_deltasigma()
    modeling_tools = ModelingTools(cluster_abundance=cluster_abundance, cluster_deltasigma=cluster_deltasigma)

    return likelihood, modeling_tools
