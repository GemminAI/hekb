"""EXP-HEKB002 Phase 1's upstream half: real MSR + real CLE, wired together.

Scope decision (recorded in `docs/RFC_ALIGNMENT.md`): "Local Model /
semantic-annotator-core / Meaning Mapper" is represented via
`meaning-space-runtime`'s own `msr.reference`-style convention — a clean,
deterministic `MeaningMeasurement` stream fed directly into a real
`MeaningSpaceRuntime` — the same pattern `meaning-space-runtime`'s own
`experiments/exp_msr_004_recovery.py` uses (`temperature=0` makes the
runtime fully deterministic by construction). This experiment does not call
into `semantic-annotator-core` or `meaning-mapper` directly: neither
produces a deterministic, dependency-light `MeaningMeasurement` without a
real model, and `msr.abi.MeaningMeasurement` is exactly the boundary those
two repositories' outputs are defined to satisfy by shape (RFC-MSR01 §4).

Everything downstream of that measurement stream is real, installed,
production code: `msr.runtime.MeaningSpaceRuntime` produces a genuine
`StabilizedTrajectory` (not a fixture), and
`cle.categorical_lift.engine.CategoricalLiftEngine` — configured with
`cle.reference`'s deterministic strategies (the same ones
`categorical-lift-engine/experiments/exp_cle_005_runtime_validation.py`
validates) — lifts it into a genuine `cle.abi.outputs.HEKBCommitCandidate`.
Neither `msr` nor `cle` source was modified; both are installed editable
into this repository's `.venv` for `experiments/` use only (see
`docs/RFC_ALIGNMENT.md`, "Gate dependency: msr, cle").
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from cle.abi.outputs import HEKBCommitCandidate
from cle.categorical_lift.engine import CategoricalLiftEngine
from cle.reference import (
    ReferenceCategoryConstructor,
    ReferenceCommitCandidateBuilder,
    ReferenceConceptDiscovery,
    ReferenceCrystallizer,
    ReferenceKnowledgeDeltaGenerator,
)
from msr.abi import MeaningMeasurement, MeaningState, StabilizedTrajectory
from msr.field import DEFAULT_BASIN_RADIUS, FieldPrior
from msr.host import MSRHost
from msr.reference import RecordingKernel
from msr.runtime import MeaningSpaceRuntime

FRAME = "exp-hekb-002"
DIMENSION = 2
STEP_NS = 50_000_000
WELL_MEAN = np.array([2.0, -1.0])
SETTLE_VARIANCE = 0.05
SETTLE_STEP_BUDGET = 30


@dataclass(frozen=True, slots=True)
class UpstreamResult:
    """What Phase 1's upstream half produced, for the orchestrator to persist."""

    trajectory: StabilizedTrajectory
    commit_candidates: tuple[HEKBCommitCandidate, ...]


def _settle_to_stabilized_trajectory(prior: FieldPrior) -> StabilizedTrajectory:
    """Feed a clean, deterministic measurement stream at the well mean until
    MSR's own `StabilizationDetector` confirms a genuine quiescent dwell —
    not a hand-fabricated trajectory. Raises if the budget is exhausted
    first (there is no legitimate reason a clean, on-well stream should not
    stabilize; a budget failure is a real defect, not swallowed silently).
    """
    host = MSRHost(
        runtime=MeaningSpaceRuntime(frame_id=FRAME, dimension=DIMENSION, prior=prior),
        kernel=RecordingKernel(),
    )
    for index in range(SETTLE_STEP_BUDGET):
        measurement = MeaningMeasurement.isotropic(
            f"exp-hekb-002-settle-{index}",
            FRAME,
            WELL_MEAN.tolist(),
            SETTLE_VARIANCE,
            index * STEP_NS,
        )
        result = host.ingest(measurement)
        if result.stabilized is not None:
            return result.stabilized
    raise AssertionError(
        f"clean measurement stream failed to stabilize within {SETTLE_STEP_BUDGET} steps"
    )


def build_field_prior() -> FieldPrior:
    """An *empty* field: no well exists yet at `WELL_MEAN`.

    Deliberate — a trajectory settling into an already-known well
    (`basin_id` set from the first step) is a *reinforcement*, which CLE's
    `ReferenceConceptDiscovery` lifts into a `ConceptDelta` (only a
    `centroid_shift`, no absolute geometry to rebuild a well from). Phase 5
    needs a genuinely *novel* discovery — `StabilizedTrajectory.is_novel`
    `True`, `basin_id` `None` — so CLE emits a full `Concept` (absolute
    `centroid`/`hessian`), the only shape `msr.adapters.hekb.well_from_concept`
    can turn back into a `GaussianWell`.
    """
    return FieldPrior(FRAME, DIMENSION, (), basin_radius=DEFAULT_BASIN_RADIUS)


def build_cle_engine() -> CategoricalLiftEngine:
    """The exact reference-strategy configuration validated by
    `categorical-lift-engine`'s own EXP-Ubuntu005."""
    return CategoricalLiftEngine(
        concept_discovery=ReferenceConceptDiscovery(),
        category_constructor=ReferenceCategoryConstructor(enabled=False),
        crystallizer=ReferenceCrystallizer(),
        knowledge_delta_generator=ReferenceKnowledgeDeltaGenerator(),
        commit_candidate_builder=ReferenceCommitCandidateBuilder(),
    )


def run_upstream() -> UpstreamResult:
    prior = build_field_prior()
    trajectory = _settle_to_stabilized_trajectory(prior)
    engine = build_cle_engine()
    candidates = engine.lift(trajectory, hekb_context=None)
    return UpstreamResult(trajectory=trajectory, commit_candidates=candidates)


def state_dicts(trajectory: StabilizedTrajectory) -> tuple[dict[str, object], ...]:
    """Deterministic, numpy-free view of a trajectory's states (for the
    report / result JSON, not for any control-flow decision)."""

    def _one(state: MeaningState) -> dict[str, object]:
        return state.as_dict()

    return tuple(_one(state) for state in trajectory.states)


__all__ = [
    "UpstreamResult",
    "build_cle_engine",
    "build_field_prior",
    "run_upstream",
    "state_dicts",
]
