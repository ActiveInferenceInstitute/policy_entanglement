"""Production-harness conformance tests for ``gnn/production_ensemble.gnn.md``.

The directives these tests enforce:

* the **production** K-stream ensemble configuration of the pymdp harness
  (:func:`simulation.builders.make_ising_ensemble` under the
  :mod:`simulation.hyperparameters` constants) is *specified in GNN*
  (``gnn/production_ensemble.gnn.md``), and
* the specification is *verified against* the harness arrays elementwise, so
  drift between the declarative source and ``src/simulation`` fails the suite.

No mocks: every check parses the shipped spec and compares real arrays.  The
comparison is exact (zero tolerance) because every production array is a small
rational matrix.  Negative controls prove the comparison is non-vacuous: a
control-slice swap in the spec must change the residual, and a perturbed
reference build must be rejected.
"""

from __future__ import annotations

import importlib.util
import json
from dataclasses import replace
from pathlib import Path

import numpy as np
import pytest

from gnn.bridge import stream_cardinality
from gnn.harness import (
    conformance_negative_control,
    conformance_report,
    ensemble_from_gnn,
    harness_config,
    per_stream_specs,
    production_ensemble,
)
from gnn.model import GnnModel, GnnVariable
from gnn.parser import parse_gnn_file
from gnn.runner import CONFORMANCE_SIDECAR_NAME, run
from simulation.builders import (
    ising_coupling_tensor,
    make_ising_ensemble,
    two_action_swap_transitions,
    two_state_identity_likelihood,
)
from simulation.hyperparameters import (
    MULTI_K_VALUES,
    PYMDP_ENSEMBLE_COUPLING_LAMBDA,
    PYMDP_ENSEMBLE_GAMMA,
    PYMDP_ENSEMBLE_K,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
GNN_DIR = PROJECT_ROOT / "gnn"
PRODUCTION = GNN_DIR / "production_ensemble.gnn.md"


@pytest.fixture(scope="module")
def production_model() -> GnnModel:
    return parse_gnn_file(PRODUCTION)


def _mutated(model: GnnModel, variable: GnnVariable) -> GnnModel:
    return replace(model, variables={**model.variables, variable.name: variable})


def test_declared_parameters_are_the_harness_constants(production_model: GnnModel) -> None:
    """Every declared ``ModelParameters`` entry mirrors the hyperparameters constants."""
    params = production_model.model_parameters
    assert int(params["num_streams"]) == PYMDP_ENSEMBLE_K
    assert float(params["gamma"]) == PYMDP_ENSEMBLE_GAMMA
    assert float(params["coupling_amplitude"]) == PYMDP_ENSEMBLE_COUPLING_LAMBDA
    assert tuple(int(part) for part in params["multi_k_stream_counts"].split(",")) == MULTI_K_VALUES
    assert int(params["num_states_per_stream"]) == 2
    assert int(params["num_observations_per_stream"]) == 2
    assert int(params["num_controls_per_stream"]) == 2


def test_declared_cardinality_matches_the_gnn_stream_declaration(production_model: GnnModel) -> None:
    """The declared policy cardinality is the one the bridge reads from ``pi1``."""
    assert int(production_model.model_parameters["policy_cardinality_per_stream"]) == stream_cardinality(
        production_model
    )


def test_stream_factors_are_the_declared_builder_primitives(production_model: GnnModel) -> None:
    """Each declared stream factor equals the builder primitive it names."""
    reference = production_ensemble()
    hold_swap = two_action_swap_transitions(2)
    identity = two_state_identity_likelihood(2)
    prior = np.full(2, 0.5, dtype=np.float64)
    preference = np.array([0.0, 1.0], dtype=np.float64)
    for index, stream in enumerate(reference.streams):
        assert stream.name == f"stream_{index}"
        assert np.array_equal(stream.A, identity)
        assert np.array_equal(stream.B, hold_swap)
        assert np.array_equal(stream.C, preference)
        assert np.array_equal(stream.D, prior)


def test_gnn_ensemble_matches_the_production_build(production_model: GnnModel) -> None:
    """The core drift gate: the spec's reconstruction equals the harness build exactly."""
    report = conformance_report(production_model, production_ensemble())
    assert report.gnn_num_streams == report.reference_num_streams == PYMDP_ENSEMBLE_K
    assert report.gnn_policy_shape == report.reference_policy_shape == (2, 2)
    assert report.per_stream_max_abs_diff == ((0.0, 0.0, 0.0, 0.0), (0.0, 0.0, 0.0, 0.0))
    assert report.coupling_max_abs_diff == 0.0
    assert report.gamma_abs_diff == 0.0
    assert report.max_abs_diff == 0.0
    assert report.conformant is True


def test_gnn_ensemble_is_field_for_field_the_reference(production_model: GnnModel) -> None:
    """Beyond the residuals: identical stream names, dtypes, coupling, and gamma."""
    declared = ensemble_from_gnn(production_model)
    reference = production_ensemble()
    assert [stream.name for stream in declared.streams] == [stream.name for stream in reference.streams]
    for left, right in zip(declared.streams, reference.streams, strict=True):
        for factor in ("A", "B", "C", "D"):
            left_array = getattr(left, factor)
            right_array = getattr(right, factor)
            assert left_array.dtype == right_array.dtype
            assert np.array_equal(left_array, right_array)
    assert np.array_equal(declared.coupling_j, reference.coupling_j)
    assert np.array_equal(declared.coupling_kc, reference.coupling_kc)
    assert declared.gamma == reference.gamma


def test_declared_coupling_is_the_mean_zero_peak_normalized_ising_tensor(production_model: GnnModel) -> None:
    """The declared ``J`` is the builder's Ising tensor, mean-zero at the declared amplitude."""
    declared = ensemble_from_gnn(production_model).coupling_j
    assert np.array_equal(declared, ising_coupling_tensor((2, 2), scale=PYMDP_ENSEMBLE_COUPLING_LAMBDA))
    assert abs(declared.mean()) < 1e-12
    assert np.isclose(np.abs(declared).max(), PYMDP_ENSEMBLE_COUPLING_LAMBDA)


def test_conformance_report_detects_reference_drift(production_model: GnnModel) -> None:
    """A perturbed reference build is rejected (the gate is not vacuous)."""
    gamma_drift = conformance_report(production_model, production_ensemble(gamma=2.0))
    assert gamma_drift.conformant is False
    assert gamma_drift.gamma_abs_diff == 1.0

    coupling_drift = conformance_report(production_model, production_ensemble(coupling_amplitude=0.5))
    assert coupling_drift.conformant is False
    assert coupling_drift.coupling_max_abs_diff == 0.5

    stream_drift = conformance_report(production_model, production_ensemble(num_streams=3))
    assert stream_drift.conformant is False
    assert stream_drift.gnn_num_streams != stream_drift.reference_num_streams


def test_conformance_report_detects_declared_array_drift(production_model: GnnModel) -> None:
    """A perturbed declaration is rejected elementwise (C, then J)."""
    preference = production_model.variable("C1")
    drifted = _mutated(production_model, replace(preference, value=np.array([0.0, 2.0], dtype=np.float64)))
    report = conformance_report(drifted, production_ensemble())
    assert report.conformant is False
    assert report.per_stream_max_abs_diff[0][2] == 1.0
    assert report.per_stream_max_abs_diff[1][2] == 0.0

    coupling = production_model.variable("J")
    zeroed = _mutated(production_model, replace(coupling, value=np.zeros((2, 2), dtype=np.float64)))
    assert conformance_report(zeroed, production_ensemble()).coupling_max_abs_diff == 1.0


def test_conformance_negative_control_discriminates(production_model: GnnModel) -> None:
    """NEGATIVE CONTROL: swapping the declared control slices changes the residual."""
    assert conformance_negative_control(production_model, production_ensemble()) == 1.0


def test_control_swap_keeps_the_pmf_contract_intact(production_model: GnnModel) -> None:
    """The control swap is a semantics change, not a shape/stochasticity break."""
    transitions = production_model.variable("B1")
    swapped = replace(transitions, value=transitions.matrix()[:, :, ::-1])
    assert np.array_equal(swapped.matrix()[:, :, 0], two_action_swap_transitions(2)[:, :, 1])
    assert np.allclose(swapped.matrix().sum(axis=0), np.ones((2, 2)))
    # StreamSpec.validate() must accept the swapped tensor...
    assert per_stream_specs(_mutated(production_model, swapped))[0].B.shape == (2, 2, 2)
    # ...and the conformance check must still reject it.
    assert conformance_report(_mutated(production_model, swapped), production_ensemble()).max_abs_diff > 0.0


@pytest.mark.parametrize("num_streams", MULTI_K_VALUES)
def test_multi_k_family_reuses_the_declared_factors_and_coupling_rule(
    production_model: GnnModel, num_streams: int
) -> None:
    """The declared K>2 story holds: same per-stream factors, same coupling rule."""
    reference = production_ensemble(num_streams=num_streams)
    template = per_stream_specs(production_model)[0]
    assert reference.num_streams() == num_streams
    for stream in reference.streams:
        assert np.array_equal(stream.A, template.A)
        assert np.array_equal(stream.B, template.B)
        assert np.array_equal(stream.C, template.C)
        assert np.array_equal(stream.D, template.D)
    assert np.array_equal(
        reference.coupling_j,
        ising_coupling_tensor((2,) * num_streams, scale=PYMDP_ENSEMBLE_COUPLING_LAMBDA),
    )
    assert abs(reference.coupling_j.mean()) < 1e-12
    assert np.isclose(np.abs(reference.coupling_j).max(), PYMDP_ENSEMBLE_COUPLING_LAMBDA)
    assert np.array_equal(reference.coupling_kc, np.zeros((2,) * num_streams))
    assert reference.gamma == PYMDP_ENSEMBLE_GAMMA


def test_reference_build_follows_the_hyperparameters() -> None:
    """``production_ensemble`` is exactly the hyperparameter-driven builder call."""
    assert np.array_equal(
        production_ensemble().coupling_j,
        make_ising_ensemble(
            coupling_amplitude=PYMDP_ENSEMBLE_COUPLING_LAMBDA,
            gamma=PYMDP_ENSEMBLE_GAMMA,
            num_streams=PYMDP_ENSEMBLE_K,
        ).coupling_j,
    )
    override = production_ensemble(num_streams=4, coupling_amplitude=0.25, gamma=0.5)
    assert override.num_streams() == 4
    assert override.gamma == 0.5
    assert np.isclose(np.abs(override.coupling_j).max(), 0.25)


def test_harness_config_is_sourced_from_the_declarations(production_model: GnnModel) -> None:
    """``--harness`` config equals the reference arrays, and is JSON-serializable."""
    config = harness_config(production_model)
    reference = production_ensemble()
    assert config["model_section"] == production_model.section
    assert config["num_streams"] == PYMDP_ENSEMBLE_K
    assert config["policy_cardinality_per_stream"] == stream_cardinality(production_model)
    assert config["joint_coupling"] == reference.coupling_j.tolist()
    assert config["gamma"] == reference.gamma
    assert json.loads(json.dumps(config)) == config
    for index, stream in enumerate(config["streams"]):
        assert stream["name"] == reference.streams[index].name
        assert stream["num_obs"] == stream["num_states"] == stream["num_controls"] == 2
        for factor in ("A", "B", "C", "D"):
            assert stream[factor] == getattr(reference.streams[index], factor).tolist()


def test_per_stream_specs_rejects_a_model_without_declared_streams(production_model: GnnModel) -> None:
    """Guard: no streams declared -> refuse rather than emit an empty ensemble."""
    with pytest.raises(ValueError, match="no policy streams"):
        per_stream_specs(replace(production_model, variables={}, ontology={}))


def test_per_stream_specs_rejects_a_missing_factor(production_model: GnnModel) -> None:
    """Guard: a missing per-stream factor names the absent variable."""
    variables = {name: var for name, var in production_model.variables.items() if name != "B1"}
    with pytest.raises(ValueError, match="declares no per-stream factor 'B1'"):
        per_stream_specs(replace(production_model, variables=variables))


def test_per_stream_specs_rejects_a_pmf_contract_violation(production_model: GnnModel) -> None:
    """Guard: a non-stochastic declared transition is rejected with the stream named."""
    transitions = production_model.variable("B2")
    broken = replace(transitions, value=2.0 * transitions.matrix())
    with pytest.raises(ValueError, match="GNN stream 2"):
        per_stream_specs(_mutated(production_model, broken))


def test_ensemble_from_gnn_requires_matching_coupling_shape(production_model: GnnModel) -> None:
    """Guard: a coupling whose shape misses the policy space is rejected."""
    wrong = GnnVariable(name="J", dims=(3, 3), dtype="float", value=np.zeros((3, 3)))
    assert wrong.dims == (3, 3)
    with pytest.raises(ValueError, match="coupling J shape"):
        ensemble_from_gnn(_mutated(production_model, wrong))


def test_ensemble_from_gnn_defaults_gamma_to_zero_when_undeclared(production_model: GnnModel) -> None:
    """An undeclared ``gamma`` means the unweighted coupling limit."""
    variables = {name: var for name, var in production_model.variables.items() if name != "gamma"}
    assert ensemble_from_gnn(replace(production_model, variables=variables)).gamma == 0.0


def test_runner_emits_the_conformance_sidecar(tmp_path: Path) -> None:
    """The pipeline stage records the conformance evidence durably."""
    data_dir = tmp_path / "data"
    rc = run(data_dir=data_dir, fig_dir=tmp_path / "fig", gnn_dir=GNN_DIR, lean_out=tmp_path / "x.lean")
    assert rc == 0
    payload = json.loads((data_dir / CONFORMANCE_SIDECAR_NAME).read_text())
    assert payload["conformant"] is True
    assert payload["negative_control_discriminates"] is True
    assert payload["negative_control_swapped_control_max_abs_diff"] == 1.0
    assert payload["conformance"]["max_abs_diff"] == 0.0
    assert payload["declared_model_parameters"]["multi_k_stream_counts"] == "3, 4, 5"


def test_pipeline_stage_fails_on_declared_harness_drift(tmp_path: Path) -> None:
    """NON-VACUITY at the pipeline level: a drifted production spec fails the stage."""
    gnn_dir = tmp_path / "gnn"
    gnn_dir.mkdir()
    (gnn_dir / "bernoulli_toy.gnn.md").write_text((GNN_DIR / "bernoulli_toy.gnn.md").read_text())
    drifted = PRODUCTION.read_text().replace("C1={(0.0, 1.0)}", "C1={(0.0, 2.0)}")
    assert drifted != PRODUCTION.read_text()
    (gnn_dir / "production_ensemble.gnn.md").write_text(drifted)
    rc = run(data_dir=tmp_path / "data", fig_dir=tmp_path / "fig", gnn_dir=gnn_dir, lean_out=tmp_path / "x.lean")
    assert rc == 1
    payload = json.loads((tmp_path / "data" / CONFORMANCE_SIDECAR_NAME).read_text())
    assert payload["conformant"] is False
    assert payload["conformance"]["per_stream_max_abs_diff"][0]["C"] == 1.0


def test_gnn_to_pymdp_script_harness_mode(capsys: pytest.CaptureFixture[str]) -> None:
    """``scripts/gnn_to_pymdp.py --harness`` emits the production harness config."""
    spec = importlib.util.spec_from_file_location(
        "_gnn_to_pymdp_under_test", PROJECT_ROOT / "scripts" / "gnn_to_pymdp.py"
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    assert module.main(["--harness"]) == 0
    config = json.loads(capsys.readouterr().out)
    assert config["num_streams"] == PYMDP_ENSEMBLE_K
    assert config["streams"][0]["A"] == [[1.0, 0.0], [0.0, 1.0]]
    assert config["gamma"] == PYMDP_ENSEMBLE_GAMMA


def test_gnn_to_pymdp_script_default_mode_still_emits_the_policy_config(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """The pre-existing policy-level mode is unchanged (default path, no flag)."""
    spec = importlib.util.spec_from_file_location(
        "_gnn_to_pymdp_default_under_test", PROJECT_ROOT / "scripts" / "gnn_to_pymdp.py"
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    assert module.main([str(GNN_DIR / "bernoulli_toy.gnn.md")]) == 0
    config = json.loads(capsys.readouterr().out)
    assert config["num_streams"] == 2
    assert config["policy_cardinality_per_stream"] == 2
    assert config["joint_coupling"] == [[0.5, -0.5], [-0.5, 0.5]]
