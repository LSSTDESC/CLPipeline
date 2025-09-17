from .firecrown_recipes.counts_cp import MurataBinnedSpecZSelectionRecipe as MCS
from .firecrown_recipes.deltasigma_cp import MurataBinnedSpecZDeltaSigmaSelectionRecipe as MDS
from firecrown.models.cluster.deltasigma import ClusterDeltaSigma
from firecrown.models.cluster.abundance import ClusterAbundance
from firecrown.models.cluster.properties import ClusterProperty
from firecrown.likelihood.binned_cluster_number_counts import BinnedClusterNumberCounts
from firecrown.likelihood.binned_cluster_number_counts_deltasigma import BinnedClusterDeltaSigma
from firecrown.models.cluster.mass_proxy import MurataBinned
import sacc
import pyccl as ccl
import numpy as np
from firecrown.modeling_tools import ModelingTools


def counts_deltasigma_prediction_from_sacc(path, survey_nm, pivot_mass, pivot_redshift, mu_p0, mu_p1, mu_p2, sigma_p0, sigma_p1, sigma_p2, mass_parameter=False):
    s_read = sacc.Sacc.load_fits(path)

    
    hmf = ccl.halos.MassFuncDespali16()
    min_mass, max_mass = 13., 16.
    min_z, max_z = 0.2, 0.8
    cluster_deltasigma = ClusterDeltaSigma((min_mass, max_mass), (min_z, max_z), hmf)
    cluster_abundance = ClusterAbundance((min_mass, max_mass), (min_z, max_z), hmf)
    cosmo_ccl = ccl.Cosmology(
    Omega_c=0.2052,
    Omega_b=0.0448,
    h=0.71,
    n_s=0.963,
    sigma8=0.8,
    Omega_k=0.0,
    Neff=3.044,
    m_nu=0.0,
    w0=-1.0,
    wa=0.0,
    T_CMB=2.7255
    )
    cluster_abundance.update_ingredients(cosmo_ccl)
    cluster_deltasigma.update_ingredients(cosmo_ccl)
    
    modeling_tools = ModelingTools(cluster_abundance = cluster_abundance, cluster_deltasigma=cluster_deltasigma)
    mds = MDS()
    mds.mass_distribution.pivot_mass = np.log(10**pivot_mass)
    mds.mass_distribution.pivot_redshift = pivot_redshift
    mds.mass_distribution.log1p_pivot_redshift = np.log1p(pivot_redshift)
    mds.mass_distribution.mu_p0 = mu_p0
    mds.mass_distribution.mu_p1 = mu_p1
    mds.mass_distribution.mu_p2 = mu_p2
    mds.mass_distribution.sigma_p0 = sigma_p0
    mds.mass_distribution.sigma_p1 = sigma_p1
    mds.mass_distribution.sigma_p2 = sigma_p2
    
    mds.mass_distribution_unb.pivot_mass = np.log(10**pivot_mass)
    mds.mass_distribution_unb.pivot_redshift = pivot_redshift
    mds.mass_distribution_unb.log1p_pivot_redshift = np.log1p(pivot_redshift)
    mds.mass_distribution_unb.mu_p0 = mu_p0
    mds.mass_distribution_unb.mu_p1 = mu_p1
    mds.mass_distribution_unb.mu_p2 = mu_p2
    mds.mass_distribution_unb.sigma_p0 = sigma_p0
    mds.mass_distribution_unb.sigma_p1 = sigma_p1
    mds.mass_distribution_unb.sigma_p2 = sigma_p2

    mds.purity_distribution.ap_nc = 1.98
    mds.purity_distribution.bp_nc = 0.812
    mds.purity_distribution.ap_rc = 2.2183
    mds.purity_distribution.bp_rc = -0.6592
    
    mds.completeness_distribution.ac_nc = 1.1321
    mds.completeness_distribution.bc_nc = 0.7751
    mds.completeness_distribution.ac_mc = 13.31
    mds.completeness_distribution.bc_mc = 0.2025

    average_on = ClusterProperty.DELTASIGMA
    if mass_parameter:
        average_on |= ClusterProperty.MASS
    bin_cl_theory = BinnedClusterDeltaSigma(average_on, survey_nm, mds)
    bin_cl_theory.read(s_read)
    cluster_abundance.update_ingredients(cosmo_ccl)

    prediction = bin_cl_theory._compute_theory_vector(modeling_tools)
    data = bin_cl_theory.data_vector
    return data, prediction


