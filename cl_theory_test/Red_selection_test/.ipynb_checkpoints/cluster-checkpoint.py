"""Likelihood factory function for cluster number counts."""

import os

import pyccl as ccl
import sacc

from firecrown.likelihood.gaussian import ConstGaussian

from firecrown.likelihood.binned_cluster_number_counts import (
    BinnedClusterNumberCounts,
)

from firecrown.likelihood.likelihood import Likelihood, NamedParameters
from firecrown.modeling_tools import ModelingTools
from firecrown.models.cluster.abundance import ClusterAbundance
from firecrown.models.cluster.properties import ClusterProperty

from firecrown.models.cluster.recipes.murata_binned_spec_z_selection import (
    MurataBinnedSpecZSelectionRecipe,
)


def get_cluster_abundance() -> ClusterAbundance:
    """Creates and returns a ClusterAbundance object."""
    hmf = ccl.halos.MassFuncDespali16(mass_def="200c")
    min_mass, max_mass = 13.0, 16.0
    min_z, max_z = 0.2, 0.8
    cluster_abundance = ClusterAbundance(min_mass, max_mass, min_z, max_z, hmf)

    return cluster_abundance


def build_likelihood(
    build_parameters: NamedParameters,
) -> tuple[Likelihood, ModelingTools]:
    """Builds the likelihood for Firecrown."""
    # Pull params for the likelihood from build_parameters
    average_on = ClusterProperty.COUNTS

    survey_name = "cosmodc2"
    likelihood = ConstGaussian(
        [
            BinnedClusterNumberCounts(
                average_on, survey_name, MurataBinnedSpecZSelectionRecipe()
            ),
        ]
    )

    # Read in sacc data
    sacc_file_nm = "cosmodc2.sacc"
    sacc_path = os.path.expanduser(
        os.path.expandvars(
            "/pbs/home/e/ebarroso/CLPipeline/cl_theory_test/Red_selection_test/"
        )
    )
    sacc_data = sacc.Sacc.load_fits(os.path.join(sacc_path, sacc_file_nm))
    likelihood.read(sacc_data)
    cluster_abundance = get_cluster_abundance()
    modeling_tools = ModelingTools(
        cluster_abundance=cluster_abundance)

    return likelihood, modeling_tools
