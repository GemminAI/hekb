"""EXP-HEKB004's Cross-Modal Reconstruction Engine.

Tests A-D (specification.md section IV): given a single observation
already resolved to a real object in a real
`hekb.category.KnowledgeCategory`, recover its full Observation Bundle.
This module adds **no new retrieval algorithm** -- it computes the bundle
purely via `_semantic_closure.compute_closure` (EXP-HEKB002's real
pullback/pushout closure, reused unmodified, per explicit instruction: no
vector/embedding search anywhere) and reshapes that existing, real output
into the specification's section VI response payload shape.

Every numeric metric this module can compute (`context_economy_ratio`,
`execution_time_ms`) is computed from the real category passed in.
`reality_convergence_score`, `reconstruction_accuracy`, and
`false_convergence_rate` are left `None` with a documented reason when
their real preconditions (>=2 real modalities ingested for the same
target, a real ground-truth bundle, >=2 real distinct targets) are not
met -- never filled with an invented number.
"""

from __future__ import annotations

import dataclasses
import time
from dataclasses import dataclass
from typing import Any

from _observation_bundle import (
    CrossSubjectInvariantMatch,
    Observation,
    ObservationBundle,
    TargetObject,
)
from _semantic_closure import SemanticClosure, compute_closure
from hekb.category import KnowledgeCategory


@dataclass(frozen=True, slots=True)
class ReconstructionQuery:
    raw_input: str
    input_modality: str
    resolved_target_id: str


@dataclass(frozen=True, slots=True)
class SearchMetrics:
    """Each field is `None` unless it was actually computed below from a
    real measurement; no field is ever a target value asserted as met."""

    reality_convergence_score: float | None
    reconstruction_accuracy: float | None
    false_convergence_rate: float | None
    context_economy_ratio: float | None
    execution_time_ms: float


@dataclass(frozen=True, slots=True)
class ReconstructionResult:
    query: ReconstructionQuery
    target_object: TargetObject
    observation_bundle: ObservationBundle
    cross_subject_invariants: tuple[CrossSubjectInvariantMatch, ...]
    proof_path: tuple[str, ...]
    closure: SemanticClosure
    search_metrics: SearchMetrics


def reconstruct(
    category: KnowledgeCategory,
    relation_kind: dict[str, str],
    object_category: dict[str, str],
    query: ReconstructionQuery,
    target: TargetObject,
    observations_by_id: dict[str, Observation],
    cross_subject_invariants: tuple[CrossSubjectInvariantMatch, ...] = (),
) -> ReconstructionResult:
    """Reconstruct `target`'s Observation Bundle from its own real closure.

    `observations_by_id` maps every closure object id that is a real,
    already-ingested Observation to that `Observation` value -- the caller
    is responsible for having actually admitted those Observations as real
    objects/morphisms in `category` beforehand; this function never
    fabricates an `Observation` for an id it does not recognize, it simply
    omits it from the recovered bundle.
    """
    start = time.perf_counter()
    closure = compute_closure(category, relation_kind, object_category, query.resolved_target_id)
    elapsed_ms = (time.perf_counter() - start) * 1000.0

    bundle_observations = tuple(
        observations_by_id[obj.id] for obj in closure.objects if obj.id in observations_by_id
    )
    bundle = ObservationBundle(target=target, observations=bundle_observations)

    proof_path = (query.raw_input, *(c.formula for c in closure.derived_compositions))

    context_economy_ratio = (
        len(closure.objects) / len(category.objects) if category.objects else None
    )

    metrics = SearchMetrics(
        # Requires real geometry (mu/Sigma/kappa/lambda) from >= 2 real
        # modalities' MSR trajectories for this target -- none ingested yet.
        reality_convergence_score=None,
        # Requires a real ground-truth Observation Bundle to compare the
        # recovered one against -- not available without a real corpus.
        reconstruction_accuracy=None,
        # Requires >= 2 real, distinct Target Objects ingested together to
        # measure a false-merge rate against -- not available yet.
        false_convergence_rate=None,
        context_economy_ratio=context_economy_ratio,
        execution_time_ms=elapsed_ms,
    )

    return ReconstructionResult(
        query=query,
        target_object=target,
        observation_bundle=bundle,
        cross_subject_invariants=cross_subject_invariants,
        proof_path=proof_path,
        closure=closure,
        search_metrics=metrics,
    )


def reconstruction_payload(result: ReconstructionResult) -> dict[str, Any]:
    """Shape a `ReconstructionResult` into specification.md section VI's
    response payload shape. Every dataclass here is a plain data value, so
    `dataclasses.asdict` recursively converts each one (and its `Union`-typed
    `Observation.slice`, since `asdict` dispatches on the runtime type of
    each field, not its static annotation) without any hand-written
    per-field mapping to drift out of sync with `_observation_bundle.py`.
    """
    return {
        "query": dataclasses.asdict(result.query),
        "target_object": dataclasses.asdict(result.target_object),
        "observation_bundle": [
            dataclasses.asdict(obs) for obs in result.observation_bundle.observations
        ],
        "cross_subject_invariants": [
            dataclasses.asdict(m) for m in result.cross_subject_invariants
        ],
        "proof_path": list(result.proof_path),
        "search_metrics": dataclasses.asdict(result.search_metrics),
    }


__all__ = [
    "ReconstructionQuery",
    "ReconstructionResult",
    "SearchMetrics",
    "reconstruct",
    "reconstruction_payload",
]
