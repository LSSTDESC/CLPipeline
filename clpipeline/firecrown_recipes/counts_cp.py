"""Module for defining the classes used in the MurataBinnedSpecZ cluster recipe."""

from typing import Callable

import numpy as np
import numpy.typing as npt

from firecrown.models.cluster.abundance import ClusterAbundance
from firecrown.models.cluster.binning import NDimensionalBin
from firecrown.models.cluster.integrator.numcosmo_integrator import NumCosmoIntegrator
from firecrown.models.cluster.kernel import SpectroscopicRedshift
from firecrown.models.cluster.mass_proxy import MurataUnbinned
from firecrown.models.cluster.properties import ClusterProperty
from firecrown.models.cluster.recipes.cluster_recipe import ClusterRecipe
from firecrown.models.cluster.kernel import Completeness, Purity


class MurataBinnedSpecZSelectionRecipe(ClusterRecipe):
    """Cluster recipe with Murata19 mass-richness and spec-zs.

    This recipe uses the Murata 2019 binned mass-richness relation and assumes
    perfectly measured spec-zs.
    """

    def __init__(self) -> None:
        super().__init__()

        self.integrator = NumCosmoIntegrator()
        self.redshift_distribution = SpectroscopicRedshift()
        pivot_mass, pivot_redshift = 14.3, 0.5
        self.mass_distribution = MurataUnbinned(pivot_mass, pivot_redshift)
        self.completeness_distribution = Completeness()
        self.purity_distribution = Purity()
        self.my_updatables.append(self.mass_distribution)
        self.my_updatables.append(self.completeness_distribution)
        self.my_updatables.append(self.purity_distribution)

    def get_theory_prediction(
        self,
        cluster_theory: ClusterAbundance,
        average_on: None | ClusterProperty = None,
    ) -> Callable[
        [
            npt.NDArray[np.float64],
            npt.NDArray[np.float64],
            npt.NDArray[np.float64],
            float,
        ],
        npt.NDArray[np.float64],
    ]:
        """Get a callable that evaluates a cluster theory prediction.

        Returns a callable function that accepts mass, redshift, mass proxy limits,
        and the sky area of your survey and returns the theoretical prediction for the
        expected number of clusters.
        """

        def theory_prediction(
            mass: npt.NDArray[np.float64],
            z: npt.NDArray[np.float64],
            mass_proxy: npt.NDArray[np.float64],
            sky_area: float,
        ):
            prediction = (
                cluster_theory.comoving_volume(z, sky_area)
                * cluster_theory.mass_function(mass, z)
                * self.redshift_distribution.distribution()
                * self.mass_distribution.distribution(mass, z, mass_proxy)
                * self.completeness_distribution.distribution(mass, z)
                / self.purity_distribution.distribution(z, mass_proxy=mass_proxy)
            )

            if average_on is None:
                return prediction

            for cluster_prop in ClusterProperty:
                include_prop = cluster_prop & average_on
                if not include_prop:
                    continue
                if cluster_prop == ClusterProperty.MASS:
                    prediction *= mass
                elif cluster_prop == ClusterProperty.REDSHIFT:
                    prediction *= z
                else:
                    raise NotImplementedError(f"Average for {cluster_prop}.")

            return prediction

        return theory_prediction

    def get_function_to_integrate(
        self,
        prediction: Callable[
            [
                npt.NDArray[np.float64],
                npt.NDArray[np.float64],
                npt.NDArray[np.float64],
                float,
            ],
            npt.NDArray[np.float64],
        ],
    ) -> Callable[[npt.NDArray, npt.NDArray], npt.NDArray]:
        """Returns a callable function that can be evaluated by an integrator.

        This function is responsible for mapping arguments from the numerical integrator
        to the arguments of the theoretical prediction function.
        """

        def function_mapper(
            int_args: npt.NDArray, extra_args: npt.NDArray
        ) -> npt.NDArray[np.float64]:
            mass = int_args[:, 0]
            z = int_args[:, 1]
            mass_proxy = int_args[:, 2]

            sky_area = extra_args[0]
            return prediction(mass, z, mass_proxy, sky_area)[0]

        return function_mapper

    def evaluate_theory_prediction(
        self,
        cluster_theory: ClusterAbundance,
        this_bin: NDimensionalBin,
        sky_area: float,
        average_on: None | ClusterProperty = None,
    ) -> float:
        """Evaluate the theory prediction for this cluster recipe.

        Evaluate the theoretical prediction for the observable in the provided bin
        using the Murata 2019 binned mass-richness relation and assuming perfectly
        measured redshifts.
        """
        self.integrator.integral_bounds = [
            (cluster_theory.min_mass, cluster_theory.max_mass),
            this_bin.z_edges,
            np.array(this_bin.mass_proxy_edges),
        ]
        self.integrator.extra_args = np.array([sky_area])

        theory_prediction = self.get_theory_prediction(cluster_theory, average_on)
        prediction_wrapper = self.get_function_to_integrate(theory_prediction)

        counts = self.integrator.integrate(prediction_wrapper) * np.log(10)

        return counts
