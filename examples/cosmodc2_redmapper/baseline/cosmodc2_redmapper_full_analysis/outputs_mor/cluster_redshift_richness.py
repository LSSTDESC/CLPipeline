import os

import pyccl as ccl
import sacc

from crow import ClusterAbundance, ClusterShearProfile, kernel, mass_proxy
from crow.properties import ClusterProperty
from crow.recipes.binned_grid import GridBinnedClusterRecipe

from crow import purity_models, completeness_models
from firecrown.likelihood import (
    ConstGaussian,
    BinnedClusterShearProfile,
    BinnedClusterNumberCounts,
    Likelihood,
    NamedParameters,
)
from firecrown.modeling_tools import ModelingTools

def get_cluster_abundance() -> ClusterAbundance:
    """Creates and returns a ClusterAbundance object.""" 
    cluster_theory = ClusterAbundance(
    halo_mass_function = ccl.halos.MassFuncDespali16(mass_def="200c"),
    cosmo = ccl.CosmologyVanillaLCDM()
    )

    return cluster_theory


def get_cluster_shear_profile() -> ClusterShearProfile:
    """Creates and returns a ClusterShearProfile object."""
    cluster_theory = ClusterShearProfile(
    cosmo=ccl.CosmologyVanillaLCDM(),
    halo_mass_function = ccl.halos.MassFuncDespali16(mass_def="200c"),
    cluster_concentration=None,
    is_delta_sigma=True,
    use_beta_s_interp=False,
    two_halo_term=False,
    boost_factor=False,
    )

    return cluster_theory

def get_cluster_recipe(
    cluster_theory,
    pivot_mass: float = 14.3,
    pivot_redshift: float = 0.5,
    mass_interval=(12.0, 15.5),
    true_z_interval=(0.2, 0.8),
    is_reduced_shear = False,
    force_no_purity = False,
):
    """Creates and returns a ClusterRecipe.

    Parameters
    ----------
    cluster_theory : ClusterShearProfile or ClusterAbundance
    """
    redshift_distribution = kernel.SpectroscopicRedshift()
    completeness = completeness_models.CompletenessAguena16()
    if force_no_purity:
        purity = None
    else:
        purity = purity_models.PurityAguena16()
    if is_reduced_shear:
        cluster_theory.set_beta_parameters(10.0, 5.0)
    mass_distribution = mass_proxy.MurataUnbinned(
        pivot_log_mass=14.3,
        pivot_redshift=0.5,
    )

    recipe = GridBinnedClusterRecipe(
        redshift_grid_size = 20,
        mass_grid_size = 60,
        proxy_grid_size = 20,
        cluster_theory=cluster_theory,
        redshift_distribution=redshift_distribution,
        mass_distribution=mass_distribution,
        completeness=completeness,
        purity=purity,
        mass_interval=(12.0, 15.5),
        true_z_interval=(0.2, 0.8),
    )

    return recipe

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
    if build_parameters.get_bool('use_mean_reduced_shear', True):
        average_on |= ClusterProperty.SHEAR

    survey_name = 'cosmodc2_redmapper'
    recipe_counts = get_cluster_recipe(get_cluster_abundance())
    recipe_shear = get_cluster_recipe(get_cluster_shear_profile(), is_reduced_shear = False, force_no_purity=True)
    likelihood = ConstGaussian(
        [
            BinnedClusterNumberCounts(
                average_on, survey_name, recipe_counts
            ),
            BinnedClusterShearProfile(
                average_on, survey_name, recipe_shear
            ),
        ]
    )

    sacc_path = 'clusters_sacc_file_cov.sacc'
    sacc_data = sacc.Sacc.load_fits(sacc_path)
    likelihood.read(sacc_data)

    modeling_tools = ModelingTools()

    return likelihood, modeling_tools
