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


def _without_param(params, name):
    """Return a copy of a parameter dict with one entry removed."""
    d = dict(params)
    d.pop(name, None)
    return d


def _as_fixed(params):
    """Force every parameter in a dict to sample=False. Triplet [lo, val, hi]
    values collapse to their central value; scalars pass through unchanged."""
    fixed = {}
    for name, spec in params.items():
        values = spec["values"]
        value = values[1] if isinstance(values, (list, tuple)) else values
        fixed[name] = {"sample": False, "values": value}
    return fixed


def _as_sampled(params, spread=0.1):
    """Force every parameter in a dict to sample=True. Scalars become a
    [lo, val, hi] triplet with a modest fractional spread; existing
    triplets pass through unchanged."""
    sampled = {}
    for name, spec in params.items():
        values = spec["values"]
        if isinstance(values, (list, tuple)):
            sampled[name] = {"sample": True, "values": list(values)}
        else:
            delta = abs(values) * spread if values != 0 else spread
            sampled[name] = {"sample": True, "values": [values - delta, values, values + delta]}
    return sampled


def _section_sample_flags(ini_path, section, names):
    """Read a generated CosmoSIS parameters .ini and return, for each
    parameter name in `names`, whether it was written as a 3-value sampled
    entry ('lo val hi') or a single fixed value."""
    parser = configparser.ConfigParser()
    parser.read(ini_path)
    flags = {}
    for name in names:
        raw = parser[section][name]
        flags[name] = len(raw.split()) == 3
    return flags


def _run_full_cosmosis(tmp_path, cfg, sacc_fixture):
    """Generate all three FirecrownPipeline outputs (.py, .ini, params.ini)
    and actually invoke the `cosmosis` executable against them, returning
    the completed subprocess.CompletedProcess. This is the real-execution
    path -- not a config check. Filenames match the tags FirecrownPipeline
    is configured with in _make_stage.
    """
    sacc_in_place = tmp_path / "clusters_sacc_file_cov.sacc"
    sacc_in_place.write_bytes(sacc_fixture.read_bytes())
    stage = _make_stage(tmp_path, sacc_in_place, cfg)

    ini_path = tmp_path / "cluster_counts_mean_mass_redshift_richness.ini"
    py_path = tmp_path / "cluster_redshift_richness.py"
    params_path = tmp_path / "cluster_richness_values.ini"

    assert stage.generate_python_file(str(py_path))
    assert stage.generate_ini_file(str(ini_path))
    assert stage.generate_cosmosis_parameters_file(str(params_path))

    # cosmosis is installed as a console-script entry point, not a runnable
    # module -- `python -m cosmosis` does not work (no __main__.py).
    return subprocess.run(
        ["cosmosis", str(ini_path)],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        timeout=1800,
    )


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
# not slow -- generate_ini_file / generate_cosmosis_parameters_file don't
# execute cosmosis, just write config files)
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


def test_only_cosmo_sampled_writes_correct_priors(full_stack, tmp_path):
    """Config-level check (cheap, non-slow): when only the cosmological
    block is set to sample=True, every cosmo parameter should be written as
    a 3-value CosmoSIS range and every firecrown/MOR parameter as a single
    fixed value. This is a precondition check for the real-execution test
    below, not a substitute for it."""
    cfg = _base_firecrown_config(
        cosmological_parameters=_as_sampled(COSMOLOGICAL_PARAMETERS),
        firecrown_parameters=_as_fixed(FIRECROWN_PARAMETERS),
    )
    sacc_path = tmp_path / "clusters_sacc_file_cov.sacc"
    stage = _make_stage(tmp_path, sacc_path, cfg)

    params_path = tmp_path / "params_cosmo_only.ini"
    assert stage.generate_cosmosis_parameters_file(str(params_path))

    cosmo_flags = _section_sample_flags(
        params_path, "cosmological_parameters", COSMOLOGICAL_PARAMETERS.keys()
    )
    mor_flags = _section_sample_flags(
        params_path, "firecrown_number_counts", FIRECROWN_PARAMETERS.keys()
    )
    assert all(cosmo_flags.values()), f"expected all cosmo params sampled, got: {cosmo_flags}"
    assert not any(mor_flags.values()), f"expected all MOR params fixed, got: {mor_flags}"


def test_only_mor_sampled_writes_correct_priors(full_stack, tmp_path):
    """Inverse of the above: only the mass-observable-relation block is
    sampled, cosmology entirely fixed."""
    cfg = _base_firecrown_config(
        cosmological_parameters=_as_fixed(COSMOLOGICAL_PARAMETERS),
        firecrown_parameters=_as_sampled(FIRECROWN_PARAMETERS),
    )
    sacc_path = tmp_path / "clusters_sacc_file_cov.sacc"
    stage = _make_stage(tmp_path, sacc_path, cfg)

    params_path = tmp_path / "params_mor_only.ini"
    assert stage.generate_cosmosis_parameters_file(str(params_path))

    cosmo_flags = _section_sample_flags(
        params_path, "cosmological_parameters", COSMOLOGICAL_PARAMETERS.keys()
    )
    mor_flags = _section_sample_flags(
        params_path, "firecrown_number_counts", FIRECROWN_PARAMETERS.keys()
    )
    assert not any(cosmo_flags.values()), f"expected all cosmo params fixed, got: {cosmo_flags}"
    assert all(mor_flags.values()), f"expected all MOR params sampled, got: {mor_flags}"


# ---------------------------------------------------------------------------
# Tier 3: actually run cosmosis (full_stack + slow) -- these are the
# meaningful tests: they exercise the real firecrown parameter-binding
# path, the same one that produced the MissingSamplerParameterError /
# RuntimeError shown when purity_a_n was removed manually.
# ---------------------------------------------------------------------------

@pytest.mark.slow
def test_generated_files_run_with_test_sampler(full_stack, tmp_path, mock_cluster_sacc_dense):
    """Full smoke test with the complete baseline config: everything that's
    required is present, so this should run cleanly end to end."""
    cfg = _base_firecrown_config(sampler="test", filename=str(tmp_path / "chain.txt"))
    result = _run_full_cosmosis(tmp_path, cfg, mock_cluster_sacc_dense)
    assert result.returncode == 0, (
        f"cosmosis test-sampler run failed.\n"
        f"stdout:\n{result.stdout}\n\nstderr:\n{result.stderr}"
    )


@pytest.mark.slow
def test_only_cosmo_sampled_runs_successfully(full_stack, tmp_path, mock_cluster_sacc_dense):
    """test sampler evaluates the likelihood once regardless of the sample
    flag, so this mainly confirms that toggling sample=True/False doesn't
    accidentally drop a parameter out of the generated files -- if it did,
    this would fail the same way the purity_a_n removal did."""
    cfg = _base_firecrown_config(
        sampler="test",
        filename=str(tmp_path / "chain.txt"),
        cosmological_parameters=_as_sampled(COSMOLOGICAL_PARAMETERS),
        firecrown_parameters=_as_fixed(FIRECROWN_PARAMETERS),
    )
    result = _run_full_cosmosis(tmp_path, cfg, mock_cluster_sacc_dense)
    assert result.returncode == 0, (
        f"cosmo-only-sampled run failed.\nstdout:\n{result.stdout}\n\nstderr:\n{result.stderr}"
    )


@pytest.mark.slow
def test_only_mor_sampled_runs_successfully(full_stack, tmp_path, mock_cluster_sacc_dense):
    cfg = _base_firecrown_config(
        sampler="test",
        filename=str(tmp_path / "chain.txt"),
        cosmological_parameters=_as_fixed(COSMOLOGICAL_PARAMETERS),
        firecrown_parameters=_as_sampled(FIRECROWN_PARAMETERS),
    )
    result = _run_full_cosmosis(tmp_path, cfg, mock_cluster_sacc_dense)
    assert result.returncode == 0, (
        f"MOR-only-sampled run failed.\nstdout:\n{result.stdout}\n\nstderr:\n{result.stderr}"
    )


@pytest.mark.slow
@pytest.mark.parametrize(
    "missing_param",
    ["purity_a_n", "purity_b_n", "purity_a_logm_piv", "purity_b_logm_piv"],
)
def test_missing_purity_parameter_fails_at_runtime(
    full_stack, tmp_path, mock_cluster_sacc_dense, missing_param
):
    """Direct regression test for the failure mode you hit manually:
    removing a purity_* parameter while use_purity=True should surface
    firecrown's own MissingSamplerParameterError, naming that exact
    parameter, not an unrelated or silent failure."""
    cfg = _base_firecrown_config(
        sampler="test",
        filename=str(tmp_path / "chain.txt"),
        use_purity=True,
        firecrown_parameters=_without_param(FIRECROWN_PARAMETERS, missing_param),
    )
    result = _run_full_cosmosis(tmp_path, cfg, mock_cluster_sacc_dense)
    combined = result.stdout + result.stderr

    assert result.returncode != 0, (
        f"Expected failure with {missing_param} missing, but cosmosis exited 0.\n"
        f"stdout:\n{result.stdout}\n\nstderr:\n{result.stderr}"
    )
    assert missing_param in combined, (
        f"Expected the missing parameter name '{missing_param}' to appear in "
        f"cosmosis output, but it didn't.\nstdout:\n{result.stdout}\n\n"
        f"stderr:\n{result.stderr}"
    )


@pytest.mark.slow
@pytest.mark.parametrize(
    "missing_param",
    [
        "completeness_a_n",
        "completeness_b_n",
        "completeness_a_logm_piv",
        "completeness_b_logm_piv",
    ],
)
def test_missing_completeness_parameter_fails_at_runtime(
    full_stack, tmp_path, mock_cluster_sacc_dense, missing_param
):
    """Mirror of the purity test for use_completeness=True."""
    cfg = _base_firecrown_config(
        sampler="test",
        filename=str(tmp_path / "chain.txt"),
        use_completeness=True,
        firecrown_parameters=_without_param(FIRECROWN_PARAMETERS, missing_param),
    )
    result = _run_full_cosmosis(tmp_path, cfg, mock_cluster_sacc_dense)
    combined = result.stdout + result.stderr

    assert result.returncode != 0, (
        f"Expected failure with {missing_param} missing, but cosmosis exited 0.\n"
        f"stdout:\n{result.stdout}\n\nstderr:\n{result.stderr}"
    )
    assert missing_param in combined, (
        f"Expected the missing parameter name '{missing_param}' to appear in "
        f"cosmosis output, but it didn't.\nstdout:\n{result.stdout}\n\n"
        f"stderr:\n{result.stderr}"
    )


@pytest.mark.slow
@pytest.mark.parametrize("is_deltasigma", [True, False], ids=["deltasigma", "reduced_shear"])
def test_missing_cluster_concentration_fails_at_runtime(
    full_stack, tmp_path, mock_cluster_sacc_dense, is_deltasigma
):
    """cluster_theory_cluster_concentration is bound whenever a shear
    profile is requested (delta_sigma or reduced shear alike -- see the
    class docstring on cluster_concentration=None at construction).
    """
    cfg = _base_firecrown_config(
        sampler="test",
        filename=str(tmp_path / "chain.txt"),
        use_shear_profile=True,
        is_deltasigma=is_deltasigma,
        firecrown_parameters=_without_param(
            FIRECROWN_PARAMETERS, "cluster_theory_cluster_concentration"
        ),
    )
    result = _run_full_cosmosis(tmp_path, cfg, mock_cluster_sacc_dense)
    combined = result.stdout + result.stderr

    assert result.returncode != 0, (
        f"Expected failure with cluster_theory_cluster_concentration missing, "
        f"but cosmosis exited 0.\nstdout:\n{result.stdout}\n\nstderr:\n{result.stderr}"
    )
    assert "cluster_theory_cluster_concentration" in combined, (
        f"Expected the missing parameter name to appear in cosmosis output.\n"
        f"stdout:\n{result.stdout}\n\nstderr:\n{result.stderr}"
    )


@pytest.mark.slow
def test_selection_function_disabled_runs_without_purity_completeness_params(
    full_stack, tmp_path, mock_cluster_sacc_dense
):
    """Inverse guard for the missing-parameter tests above: when
    use_purity=False and use_completeness=False, those parameters aren't
    required at all -- removing them should NOT cause a failure. Confirms
    firecrown's requirement is genuinely conditional on the flags, not on
    the parameter dict's contents."""
    stripped = FIRECROWN_PARAMETERS
    for name in [
        "purity_a_n", "purity_b_n", "purity_a_logm_piv", "purity_b_logm_piv",
        "completeness_a_n", "completeness_b_n",
        "completeness_a_logm_piv", "completeness_b_logm_piv",
    ]:
        stripped = _without_param(stripped, name)

    cfg = _base_firecrown_config(
        sampler="test",
        filename=str(tmp_path / "chain.txt"),
        use_purity=False,
        use_completeness=False,
        firecrown_parameters=stripped,
    )
    result = _run_full_cosmosis(tmp_path, cfg, mock_cluster_sacc_dense)
    assert result.returncode == 0, (
        f"Expected success with purity/completeness disabled and their params "
        f"removed, but cosmosis failed.\nstdout:\n{result.stdout}\n\n"
        f"stderr:\n{result.stderr}"
    )