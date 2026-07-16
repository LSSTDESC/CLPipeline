"""
Tests for FirecrownPipeline.

Ordered deliberately: file-generation tests (need only `ceci_stack`) come
first, so a structural bug in the generator shows up immediately without
waiting on any full-stack/slow test. Tests that need to actually import or
execute cosmosis/firecrown/crow/pyccl are gated by `full_stack`, and the
ones that do real computation are additionally marked `slow`.

All output files are written under pytest's tmp_path.
"""
import ast
import configparser
import subprocess

import pytest

from clpipeline.firecrown_pipeline import FirecrownPipeline


COSMOLOGICAL_PARAMETERS = {
    "omega_c": {"sample": False, "values": 0.22},
    "sigma_8": {"sample": False, "values": 0.8},
    "omega_k": {"sample": False, "values": 0.0},
    "omega_b": {"sample": False, "values": 0.0448},
    "tau": {"sample": False, "values": 0.08},
    "n_s": {"sample": False, "values": 0.963},
    "h0": {"sample": False, "values": 0.71},
    "w": {"sample": False, "values": -1.0},
    "wa": {"sample": False, "values": 0.0},
}

FIRECROWN_PARAMETERS = {
    "mass_distribution_mu0": {"sample": True, "values": [2.0, 3.3439, 10.0]},
    "mass_distribution_mu1": {"sample": True, "values": [0.5, 0.9582, 2.0]},
    "mass_distribution_mu2": {"sample": True, "values": [-2.0, -0.0193, 2.0]},
    "mass_distribution_sigma0": {"sample": True, "values": [0.1, 0.5623, 2.0]},
    "mass_distribution_sigma1": {"sample": True, "values": [-0.6, 0.0455, 0.3]},
    "mass_distribution_sigma2": {"sample": True, "values": [-0.5, -0.0445, 2.0]},
    "completeness_a_n": {"sample": False, "values": 1.1321},
    "completeness_b_n": {"sample": False, "values": 0.7751},
    "completeness_a_logm_piv": {"sample": False, "values": 13.31},
    "completeness_b_logm_piv": {"sample": False, "values": 0.2025},
    "purity_a_n": {"sample": False, "values": 1.98298628209},
    "purity_b_n": {"sample": False, "values": 0.81212176229},
    "purity_a_logm_piv": {"sample": False, "values": 2.2183},
    "purity_b_logm_piv": {"sample": False, "values": -0.6592},
    "cluster_theory_cluster_concentration": {"sample": False, "values": 4},
}


def _base_firecrown_config(**overrides):
    cfg = {
        "hmf": "despali16",
        "min_mass": 12.0,
        "max_mass": 15.5,
        "min_z": 0.2,
        "max_z": 0.8,
        "mass_def": "200c",
        "use_shear_profile": True,
        "use_completeness": True,
        "use_purity": True,
        "use_grid": True,
        "is_deltasigma": True,
        "use_beta_interp": False,
        "beta_parameters": [10.0, 5.0],
        "pivot_mass": 14.3,
        "pivot_z": 0.5,
        "survey_name": "mock_survey",
        "sampler": "test",
        "filename": "output_rp/number_counts_samples.txt",
        "resume": False,
        "use_cluster_counts": True,
        "use_mean_log_mass": False,
        "use_mean_deltasigma": True,
        "emcee_walkers": 4,
        "emcee_samples": 8,
        "emcee_nsteps": 1,
        "cosmological_parameters": COSMOLOGICAL_PARAMETERS,
        "firecrown_parameters": FIRECROWN_PARAMETERS,
    }
    cfg.update(overrides)
    return cfg


def _make_stage(tmp_path, sacc_path, cfg):
    stage = FirecrownPipeline(
        {
            "config": None,
            "clusters_sacc_file_cov": str(sacc_path),
            "cluster_counts_mean_mass_redshift_richness": str(
                tmp_path / "cluster_counts_mean_mass_redshift_richness.ini"
            ),
            "cluster_redshift_richness": str(tmp_path / "cluster_redshift_richness.py"),
            "cluster_richness_values": str(tmp_path / "cluster_richness_values.ini"),
        }
    )
    stage.config.update(cfg)
    return stage


# ---------------------------------------------------------------------------
# Tier 1: file generation only (ceci_stack) -- fast, run these first
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    "overrides",
    [
        {},  # baseline: counts + shear, deltasigma, grid
        {"use_shear_profile": False, "use_mean_deltasigma": False},  # counts only
        {"use_cluster_counts": False},  # shear only
        {"use_grid": False},  # exact binned recipe instead of grid
        {"is_deltasigma": False},  # reduced shear instead of delta sigma
        {"use_completeness": False, "use_purity": False},  # no selection function
        {"use_beta_interp": True},  # beta interpolation branch
        {"two_halo_term": True, "boost_factor": True},  # extra shear terms
    ],
    ids=[
        "baseline",
        "counts_only",
        "shear_only",
        "exact_binned",
        "reduced_shear",
        "no_selection_function",
        "beta_interp",
        "two_halo_and_boost",
    ],
)
def test_generated_python_is_syntactically_valid(ceci_stack, tmp_path, overrides):
    cfg = _base_firecrown_config(**overrides)
    sacc_path = tmp_path / "clusters_sacc_file_cov.sacc"
    stage = _make_stage(tmp_path, sacc_path, cfg)

    output_path = tmp_path / f"generated_{hash(frozenset(overrides.items())) & 0xffff}.py"
    ok = stage.generate_python_file(str(output_path))
    assert ok, f"generate_python_file failed for overrides={overrides}"

    source = output_path.read_text()
    tree = ast.parse(source)  # raises SyntaxError -> test failure if invalid

    func_names = {
        node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)
    }
    assert "build_likelihood" in func_names
    assert "get_cluster_recipe" in func_names

    if cfg["use_cluster_counts"]:
        assert "get_cluster_abundance" in func_names
        assert "BinnedClusterNumberCounts" in source
    if cfg["use_shear_profile"]:
        assert "get_cluster_shear_profile" in func_names
        assert "BinnedClusterShearProfile" in source
        # cluster_concentration must always be None at construction time --
        # firecrown binds the real value later via
        # cluster_theory_cluster_concentration, see class docstring.
        assert "cluster_concentration=None" in source


def test_sacc_path_baked_in_is_basename_only(ceci_stack, tmp_path):
    """Regression test: the generated likelihood script must reference the
    sacc file by basename only, since cosmosis runs with cwd set to the
    output directory that holds the sacc file, not the directory ceci was
    invoked from."""
    cfg = _base_firecrown_config()
    nested_sacc_path = tmp_path / "some" / "nested" / "dir" / "clusters_sacc_file_cov.sacc"
    stage = _make_stage(tmp_path, nested_sacc_path, cfg)

    output_path = tmp_path / "generated_basename_check.py"
    stage.generate_python_file(str(output_path))
    source = output_path.read_text()

    assert "sacc_path = 'clusters_sacc_file_cov.sacc'" in source
    assert str(nested_sacc_path) not in source
    assert "some" not in source and "nested" not in source


# ---------------------------------------------------------------------------
# Tier 2: .ini content checks (full_stack to import cosmosis/firecrown, but
# not slow -- generate_ini_file doesn't execute either)
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("resume", [False, True])
def test_resume_flag_written_correctly(full_stack, tmp_path, resume):
    cfg = _base_firecrown_config(resume=resume, filename=str(tmp_path / "chain.txt"))
    sacc_path = tmp_path / "clusters_sacc_file_cov.sacc"
    stage = _make_stage(tmp_path, sacc_path, cfg)

    ini_path = tmp_path / "test_resume.ini"
    assert stage.generate_ini_file(str(ini_path))

    parser = configparser.ConfigParser()
    parser.read(ini_path)
    expected = "T" if resume else "F"
    assert parser["runtime"]["resume"] == expected


def test_filename_option_used_not_hardcoded_default(full_stack, tmp_path):
    custom_filename = str(tmp_path / "my_custom_chain.txt")
    cfg = _base_firecrown_config(filename=custom_filename)
    sacc_path = tmp_path / "clusters_sacc_file_cov.sacc"
    stage = _make_stage(tmp_path, sacc_path, cfg)

    ini_path = tmp_path / "test_filename.ini"
    stage.generate_ini_file(str(ini_path))

    parser = configparser.ConfigParser()
    parser.read(ini_path)
    assert parser["output"]["filename"] == custom_filename


# ---------------------------------------------------------------------------
# Tier 3: actually run cosmosis (full_stack + slow) -- only meaningful once
# tier 1/2 above are already green.
# ---------------------------------------------------------------------------

@pytest.mark.slow
def test_generated_files_run_with_test_sampler(full_stack, tmp_path, mock_cluster_sacc_dense):
    """Full smoke test: generate all three FirecrownPipeline outputs, run
    the `cosmosis` command with sampler=test against them, and check it
    exits cleanly.

    cosmosis is installed as a console-script entry point, not a runnable
    module -- `python -m cosmosis` does not work (no __main__.py). Invoke
    the `cosmosis` executable directly instead.
    """
    sacc_in_place = tmp_path / "clusters_sacc_file_cov.sacc"
    sacc_in_place.write_bytes(mock_cluster_sacc_dense.read_bytes())

    cfg = _base_firecrown_config(sampler="test", filename=str(tmp_path / "chain.txt"))
    stage = _make_stage(tmp_path, sacc_in_place, cfg)

    ini_path = tmp_path / "cluster_counts_mean_mass_redshift_richness.ini"
    py_path = tmp_path / "cluster_redshift_richness.py"
    params_path = tmp_path / "cluster_richness_values.ini"

    assert stage.generate_python_file(str(py_path))
    assert stage.generate_ini_file(str(ini_path))
    assert stage.generate_cosmosis_parameters_file(str(params_path))

    result = subprocess.run(
        ["cosmosis", str(ini_path)],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        timeout=1800,
    )
    assert result.returncode == 0, (
        f"cosmosis test-sampler run failed.\n"
        f"stdout:\n{result.stdout}\n\nstderr:\n{result.stderr}"
    )
