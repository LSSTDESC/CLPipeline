import numpy as np
import pandas as pd
import GCRCatalogs
from crow import mass_proxy
import pyarrow.parquet as pq
import pyarrow as pa

from astropy.table import Table

# Read the FITS file into a table
catalog = Table.read("/sps/lsst/users/maguena/cats/dc2/cosmoDC2_v1.1.4/extragal/full/halos/halos_m200c_13.0.fits")

# ----------------------------
# Murata model
# ----------------------------
m_pivot = 14.3
z_pivot = 0.5

mass_richness = mass_proxy.MurataUnbinned(m_pivot, z_pivot)

mass_richness.parameters["mu0"] = 3.2
mass_richness.parameters["mu1"] = 0.8
mass_richness.parameters["mu2"] = 0.1

mass_richness.parameters["sigma0"] = 0.5
mass_richness.parameters["sigma1"] = 0.01
mass_richness.parameters["sigma2"] = 0.02

rng = np.random.default_rng()

# ----------------------------
# Output parquet writer
# ----------------------------
output_file = "/sps/lsst/users/ebarroso/CLPipeline/examples/cosmodc2_with_richness.parquet"
    
redshift = catalog["redshift_true"]
halo_mass = catalog["m200c"]
log10_mass = np.log10(halo_mass)

mu_ln = mass_richness.get_ln_mass_proxy_mean(log10_mass, redshift)
sigma_ln = mass_richness.get_ln_mass_proxy_sigma(log10_mass, redshift)
ln_richness = rng.normal(mu_ln, sigma_ln)

df = pd.DataFrame(
    {
        "redshift": redshift,
        "halo_mass": halo_mass,
        "log10_halo_mass": log10_mass,
        "richness": np.exp(ln_richness),
    }
)

table = pa.Table.from_pandas(df, preserve_index=False)

writer = pq.ParquetWriter(output_file, table.schema)

writer.write_table(table)

writer.close()

print(f"Saved richness catalog to {output_file}")

