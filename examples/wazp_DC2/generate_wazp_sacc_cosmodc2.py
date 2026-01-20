import math
import itertools

import numpy as np

from numcosmo_py import Nc
from numcosmo_py import Ncm

from astropy.table import Table

from astropy.io import fits
from scipy import stats
from typing import Any
import sacc

file_path = '/sps/lsst/groups/clusters/wazp_validation_project/DC2_run2.2i_dr6/photoz/tpz/dc2_tpz_T500k.pointEstimateMags/zband/wazp_clusters.fits'#'/sps/lsst/groups/clusters/wazp_validation_project/cosmoDC2_v1.1.4/zgauss_0.01/iband/wazp_clusters.fits'
table = Table.read(file_path)
# SNR>6 , RICHNESS>>10, REDSHIFT 0.05 to 1.07, MASS
data_table = table[table['snr'] > 6.0]
data_table = data_table[data_table['zp'] > 0.05]
data_table = data_table[data_table['zp'] < 1.07]
data_table = data_table[data_table['n200'] > 20]

print(data_table.colnames, len(data_table))

area = 300 

cluster_z = data_table["zp"]
cluster_richness = np.log10(data_table["n200"])

N_richness = 3   # number of richness bins
N_z = 3  # number of redshift bins

cluster_counts, z_edges, richness_edges, _ = stats.binned_statistic_2d(
    cluster_z, cluster_richness, None, "count", bins=[N_z, N_richness]
)
print(cluster_counts)
print(np.sum(cluster_counts))
covariance = np.diag(cluster_counts.flatten())
print(np.mean(cluster_z), np.min(cluster_z))
s_count = sacc.Sacc()
bin_z_labels = []
bin_richness_labels = []

survey_name = "dc2_wazp"
s_count.add_tracer("survey", survey_name, area)

for i, z_bin in enumerate(zip(z_edges[:-1], z_edges[1:])):
    lower, upper = z_bin
    bin_z_label = f"bin_z_{i}"
    s_count.add_tracer("bin_z", bin_z_label, lower, upper)
    bin_z_labels.append(bin_z_label)

for i, richness_bin in enumerate(zip(richness_edges[:-1], richness_edges[1:])):
    lower, upper = richness_bin
    bin_richness_label = f"rich_{i}"
    s_count.add_tracer("bin_richness", bin_richness_label, lower, upper)
    bin_richness_labels.append(bin_richness_label)

#  pylint: disable-next=no-member
cluster_count = sacc.standard_types.cluster_counts

counts_and_edges = zip(
    cluster_counts.flatten(), itertools.product(bin_z_labels, bin_richness_labels)
)


for counts, (bin_z_label, bin_richness_label) in counts_and_edges:
    s_count.add_data_point(
        cluster_count, (survey_name, bin_richness_label, bin_z_label), int(counts)
    )
s_count.add_covariance(covariance)
s_count.to_canonical_order()
s_count.save_fits("outputs/clusters_sacc_file_cov.sacc", overwrite=True)
s_count.save_fits("cluster_sacc_catalog.sacc", overwrite=True)
