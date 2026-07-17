"""
Tests for TJPCovPipeline.

TJPCovPipeline.run() always does real covariance computation (tjpcov/pyccl/
crow, no dry-run mode exists), so every test here needs the `full_stack`
fixture and is marked `slow`. All output files are written under pytest's
tmp_path, nothing needs manual cleanup.
"""
import numpy as np
import pytest
import sacc
import yaml

from clpipeline.tjpcov_pipeline import TJPCovPipeline
from .conftest import run_ceci_stage

# cluster_counts tracers never carry a radius bin (unlike
# cluster_delta_sigma), so radius-keyed lookups against them are
# structurally empty and SACC warns on it. Expected, not a bug.
pytestmark = pytest.mark.filterwarnings(
    "ignore:Empty index selected.*:UserWarning"
)


def _base_tjpcov_config(cosmo_parameters, mor_parameters, **overrides):
    cfg = {
        "replace_tjpcov_cov": True,
        "sel_func": True,
        "wazp_catalog": False,
        "diagonal_shear_covariance": True,
        "use_mpi": False,
        "do_xi": False,
        "cov_type": ["ClusterCountsGaussian", "ClusterCountsSSC"],
        "cosmo": "set",
        "parameters": cosmo_parameters,
        "photo-z": {"sigma_0": 0.05},
        "mor_parameters": mor_parameters,
    }
    cfg.update(overrides)
    return cfg


def _run_tjpcov_stage(input_sacc_path, output_sacc_path, tjpcov_cfg):
    stage = TJPCovPipeline(
        {
            "config": None,
            "clusters_sacc_file": str(input_sacc_path),
            "clusters_sacc_file_cov": str(output_sacc_path),
        }
    )
    stage.config.update(tjpcov_cfg)
    stage.run()
    return sacc.Sacc.load_fits(str(output_sacc_path))


def _write_stage_yaml(tmp_path, stage_name, cfg):
    config_path = tmp_path / "stage_config.yml"
    with open(config_path, "w") as f:
        yaml.safe_dump({stage_name: cfg}, f)
    return config_path


def _diag_block(cov, idx):
    idx = np.asarray(sorted(idx))
    return cov[np.ix_(idx, idx)]


def _radius_group_indices(sacc_obj, data_type):
    """Group data point indices by (survey, richness, z) tracer combo."""
    data_points = sacc_obj.get_data_points(data_type=data_type)
    groups = {}
    for dp in data_points:
        key = dp.tracers[:3]
        idx = sacc_obj.indices(data_type=data_type, tracers=dp.tracers)[0]
        groups.setdefault(key, set()).add(idx)
    return groups


@pytest.mark.slow
def test_dense_merge_preserves_off_diagonal(
    full_stack, tmp_path, mock_cluster_sacc_dense, mock_cosmo_parameters, mock_mor_parameters
):
    """diagonal_shear_covariance=False must preserve radius-radius correlation."""
    output_path = tmp_path / "cov_dense_kept.sacc"
    cfg = _base_tjpcov_config(
        mock_cosmo_parameters, mock_mor_parameters, diagonal_shear_covariance=False
    )
    out = _run_tjpcov_stage(mock_cluster_sacc_dense, output_path, cfg)

    cds = sacc.standard_types.cluster_delta_sigma
    groups = _radius_group_indices(out, cds)
    idx = next(iter(groups.values()))
    block = _diag_block(out.covariance.covmat, idx)
    off_diag_max = np.max(np.abs(block - np.diag(np.diag(block))))
    assert off_diag_max > 0, "expected preserved radius-radius correlation"


@pytest.mark.slow
def test_diagonal_only_merge_drops_off_diagonal(
    full_stack, tmp_path, mock_cluster_sacc_dense, mock_cosmo_parameters, mock_mor_parameters
):
    """diagonal_shear_covariance=True must strip off-diagonal terms."""
    output_path = tmp_path / "cov_diag_only.sacc"
    cfg = _base_tjpcov_config(
        mock_cosmo_parameters, mock_mor_parameters, diagonal_shear_covariance=True
    )
    out = _run_tjpcov_stage(mock_cluster_sacc_dense, output_path, cfg)

    cds = sacc.standard_types.cluster_delta_sigma
    groups = _radius_group_indices(out, cds)
    idx = next(iter(groups.values()))
    block = _diag_block(out.covariance.covmat, idx)
    off_diag_max = np.max(np.abs(block - np.diag(np.diag(block))))
    assert off_diag_max == 0.0, "expected off-diagonal terms stripped"
    assert np.all(np.diag(block) > 0), "variances should still be kept"


@pytest.mark.slow
def test_counts_only_input_completes_without_merge(
    full_stack, tmp_path, mock_cluster_sacc_counts_only, mock_cosmo_parameters, mock_mor_parameters
):
    """Counts-only input has nothing to merge; stage still completes."""
    output_path = tmp_path / "cov_counts_only.sacc"
    cfg = _base_tjpcov_config(mock_cosmo_parameters, mock_mor_parameters)
    out = _run_tjpcov_stage(mock_cluster_sacc_counts_only, output_path, cfg)

    assert out.get_data_types() == [sacc.standard_types.cluster_counts]
    assert out.covariance is not None


@pytest.mark.slow
def test_mixed_input_data_types_preserved(
    full_stack, tmp_path, mock_cluster_sacc_dense, mock_cosmo_parameters, mock_mor_parameters
):
    """Both counts and delta_sigma should still be present in the output."""
    output_path = tmp_path / "cov_mixed.sacc"
    cfg = _base_tjpcov_config(mock_cosmo_parameters, mock_mor_parameters)
    out = _run_tjpcov_stage(mock_cluster_sacc_dense, output_path, cfg)

    assert set(out.get_data_types()) == {
        sacc.standard_types.cluster_counts,
        sacc.standard_types.cluster_delta_sigma,
    }


@pytest.mark.slow
def test_ssc_replaced_counts_variance_at_least_poisson(
    full_stack, tmp_path, mock_cluster_sacc_dense, mock_cosmo_parameters, mock_mor_parameters
):
    """SSC-replaced counts variance must be >= pure Poisson variance."""
    output_path = tmp_path / "cov_ssc_check.sacc"
    cfg = _base_tjpcov_config(
        mock_cosmo_parameters, mock_mor_parameters, replace_tjpcov_cov=True
    )
    out = _run_tjpcov_stage(mock_cluster_sacc_dense, output_path, cfg)

    cc = sacc.standard_types.cluster_counts
    counts_points = out.get_data_points(data_type=cc)

    for dp in counts_points:
        idx = out.indices(data_type=cc, tracers=dp.tracers)[0]
        replaced_variance = out.covariance.covmat[idx, idx]
        poisson_variance = dp.value
        assert replaced_variance >= poisson_variance, (
            f"SSC-replaced variance ({replaced_variance}) < Poisson "
            f"variance ({poisson_variance}) for tracers {dp.tracers}."
        )


@pytest.mark.slow
def test_diagonal_shear_covariance_is_noop_for_counts_only(
    full_stack, tmp_path, mock_cluster_sacc_counts_only, mock_cosmo_parameters, mock_mor_parameters
):
    """Flag should have zero effect when there's no shear data."""
    cfg_true = _base_tjpcov_config(
        mock_cosmo_parameters, mock_mor_parameters, diagonal_shear_covariance=True
    )
    cfg_false = _base_tjpcov_config(
        mock_cosmo_parameters, mock_mor_parameters, diagonal_shear_covariance=False
    )
    out_true = _run_tjpcov_stage(
        mock_cluster_sacc_counts_only, tmp_path / "cov_true.sacc", cfg_true
    )
    out_false = _run_tjpcov_stage(
        mock_cluster_sacc_counts_only, tmp_path / "cov_false.sacc", cfg_false
    )
    np.testing.assert_allclose(
        out_true.covariance.covmat, out_false.covariance.covmat
    )


@pytest.mark.slow
def test_empty_index_warning_only_from_cluster_counts_lookup(
    full_stack, tmp_path, mock_cluster_sacc_dense, mock_cosmo_parameters, mock_mor_parameters
):
    """cluster_delta_sigma radius groups must never be empty."""
    cfg = _base_tjpcov_config(mock_cosmo_parameters, mock_mor_parameters)
    output_path = tmp_path / "cov_warning_check.sacc"
    out = _run_tjpcov_stage(mock_cluster_sacc_dense, output_path, cfg)

    cds = sacc.standard_types.cluster_delta_sigma
    groups = _radius_group_indices(out, cds)
    assert all(len(idx) > 0 for idx in groups.values()), (
        "cluster_delta_sigma tracer group came back empty"
    )


# ---------------------------------------------------------------------------
# CLI dispatch (python -m clpipeline), not direct instantiation
# ---------------------------------------------------------------------------

@pytest.mark.slow
def test_cli_invocation_produces_valid_covariance(
    full_stack, tmp_path, mock_cluster_sacc_dense, mock_cosmo_parameters, mock_mor_parameters
):
    """Runs TJPCovPipeline through the actual CLI entry point."""
    cfg = _base_tjpcov_config(mock_cosmo_parameters, mock_mor_parameters)
    config_path = _write_stage_yaml(tmp_path, "TJPCovPipeline", cfg)
    output_path = tmp_path / "cov_cli.sacc"

    result = run_ceci_stage(
        module="clpipeline",
        stage_name="TJPCovPipeline",
        config_path=config_path,
        io_args={
            "clusters_sacc_file": str(mock_cluster_sacc_dense),
            "clusters_sacc_file_cov": str(output_path),
        },
        cwd=tmp_path,
    )
    assert result.returncode == 0, f"stdout:\n{result.stdout}\n\nstderr:\n{result.stderr}"

    out = sacc.Sacc.load_fits(str(output_path))
    assert out.covariance is not None