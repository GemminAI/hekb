"""EXP-HEKB005's Visual Observation Bundle Recovery Engine.

Tests A-D (specification.md section IV): given a single observation
already resolved to a real object in a real
`hekb.category.KnowledgeCategory`, recover its full visual Observation
Bundle. Exactly like EXP-HEKB004's `_cross_modal_reconstruction.py`, this
module adds **no new retrieval algorithm** -- every recovery is computed
via `_semantic_closure.compute_closure` (EXP-HEKB002's real
pullback/pushout closure, reused unmodified) over real
`KnowledgeRelation`s built from the real corpus. No vector or embedding
search anywhere.

Unlike EXP-HEKB004, real observations exist behind every ingested node
here, so `observation_completeness` (C_obs(Q)) and
`weighted_observation_completeness` (C_w(Q)) -- specification.md section
III.5/III.6 -- are real, computed numbers, not `None`.
`visual_convergence_score` stays `None`: it requires real geometry
(mu/Sigma/kappa) from a real image-to-meaning measurement, and no such
model exists anywhere in this workspace (the same "meaning-mapper doesn't
exist" gap every EXP-HEKB experiment has recorded).
"""

from __future__ import annotations

import dataclasses
import time
from dataclasses import dataclass
from typing import Any

from _semantic_closure import SemanticClosure, compute_closure
from _visual_observation_bundle import (
    CrossSubjectInvariantMatch,
    ObservationBundle,
    TargetObject,
    VisualObservation,
)
from hekb.category import KnowledgeCategory

TECHNIQUE_VOCABULARY: tuple[str, ...] = (
    "sfumato",
    "chiaroscuro",
    "impasto",
    "camera obscura",
    "pointillism",
    "impressionism",
    "tenebrism",
    "grisaille",
    "underpainting",
    "glazing",
)


@dataclass(frozen=True, slots=True)
class ReconstructionQuery:
    raw_input: str
    input_modality: str
    resolved_target_id: str


@dataclass(frozen=True, slots=True)
class CompletenessResult:
    observation_completeness: float
    weighted_observation_completeness: float
    recovered_count: int
    ground_truth_count: int
    recovered_weight: float
    ground_truth_weight: float


@dataclass(frozen=True, slots=True)
class SearchMetrics:
    """Each field is `None` unless it was actually computed below from a
    real measurement; no field is ever a target value asserted as met."""

    visual_convergence_score: float | None
    observation_completeness: float | None
    weighted_observation_completeness: float | None
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
    completeness: CompletenessResult


def compute_completeness(
    recovered: tuple[VisualObservation, ...],
    ground_truth: tuple[VisualObservation, ...],
) -> CompletenessResult:
    """C_obs(Q) and C_w(Q), specification.md section III.5/III.6, computed
    directly from real `VisualObservation.source_id`/`importance_weight`
    values -- `ground_truth` is every real observation actually ingested
    for this work (see `_real_visual_extractors.extract_observations_for_work`),
    not a hypothetical maximum."""
    recovered_ids = {o.source_id for o in recovered}
    ground_truth_ids = {o.source_id for o in ground_truth}
    recovered_count = len(recovered_ids & ground_truth_ids)
    ground_truth_count = len(ground_truth_ids)
    observation_completeness = recovered_count / ground_truth_count if ground_truth_count else 0.0

    ground_truth_weight = sum(o.importance_weight for o in ground_truth)
    recovered_weight = sum(
        o.importance_weight for o in ground_truth if o.source_id in recovered_ids
    )
    weighted_observation_completeness = (
        recovered_weight / ground_truth_weight if ground_truth_weight else 0.0
    )
    return CompletenessResult(
        observation_completeness=observation_completeness,
        weighted_observation_completeness=weighted_observation_completeness,
        recovered_count=recovered_count,
        ground_truth_count=ground_truth_count,
        recovered_weight=recovered_weight,
        ground_truth_weight=ground_truth_weight,
    )


def reconstruct(
    category: KnowledgeCategory,
    relation_kind: dict[str, str],
    object_category: dict[str, str],
    query: ReconstructionQuery,
    target: TargetObject,
    observations_by_id: dict[str, VisualObservation],
    ground_truth_observations: tuple[VisualObservation, ...],
    cross_subject_invariants: tuple[CrossSubjectInvariantMatch, ...] = (),
) -> ReconstructionResult:
    start = time.perf_counter()
    closure = compute_closure(category, relation_kind, object_category, query.resolved_target_id)
    elapsed_ms = (time.perf_counter() - start) * 1000.0

    bundle_observations = tuple(
        observations_by_id[obj.id] for obj in closure.objects if obj.id in observations_by_id
    )
    bundle = ObservationBundle(target=target, observations=bundle_observations)
    completeness = compute_completeness(bundle_observations, ground_truth_observations)

    proof_path = (query.raw_input, *(c.formula for c in closure.derived_compositions))

    context_economy_ratio = (
        len(closure.objects) / len(category.objects) if category.objects else None
    )

    metrics = SearchMetrics(
        # Requires real geometry (mu/Sigma/kappa) from a real
        # image-to-meaning measurement; no such model exists anywhere in
        # this workspace -- see specification.md "Implementation Status".
        visual_convergence_score=None,
        observation_completeness=completeness.observation_completeness,
        weighted_observation_completeness=completeness.weighted_observation_completeness,
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
        completeness=completeness,
    )


def reconstruction_payload(result: ReconstructionResult) -> dict[str, Any]:
    """Shape a `ReconstructionResult` into specification.md section VI's
    response payload shape, via `dataclasses.asdict` exactly as
    EXP-HEKB004's `_cross_modal_reconstruction.reconstruction_payload` did."""
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
        "completeness": dataclasses.asdict(result.completeness),
    }


def check_disambiguation(
    category: KnowledgeCategory,
    relation_kind: dict[str, str],
    object_category: dict[str, str],
    target_a_id: str,
    target_b_id: str,
) -> dict[str, Any]:
    """Test D: ingest two distinct real works into the same category and
    verify their closures share no object -- a real, checkable
    disambiguation test, not an asserted `0.0%`."""
    closure_a = compute_closure(category, relation_kind, object_category, target_a_id)
    closure_b = compute_closure(category, relation_kind, object_category, target_b_id)
    ids_a = {obj.id for obj in closure_a.objects}
    ids_b = {obj.id for obj in closure_b.objects}
    overlap = sorted(ids_a & ids_b)
    smaller = min(len(ids_a), len(ids_b))
    false_convergence_rate = len(overlap) / smaller if smaller else 0.0
    return {
        "target_a": target_a_id,
        "target_b": target_b_id,
        "closure_a_size": len(ids_a),
        "closure_b_size": len(ids_b),
        "overlap_object_ids": overlap,
        "false_convergence_rate": false_convergence_rate,
        "disambiguated": len(overlap) == 0,
    }


def find_shared_technique_terms(work_texts: dict[str, str]) -> dict[str, tuple[str, ...]]:
    """Real, generic substring search over real ingested text (Wiki +
    Critique) for each term in `TECHNIQUE_VOCABULARY`, restricted to terms
    that real-text-match at least two distinct works. This is the entire
    "cross-subject technique invariant" discovery mechanism -- a term not
    actually found in >= 2 works' real text produces no link; nothing here
    is asserted from outside knowledge of art history.
    """
    lowered = {work_id: text.lower() for work_id, text in work_texts.items()}
    hits: dict[str, tuple[str, ...]] = {}
    for term in TECHNIQUE_VOCABULARY:
        matched = tuple(sorted(work_id for work_id, text in lowered.items() if term in text))
        if len(matched) >= 2:
            hits[term] = matched
    return hits


__all__ = [
    "TECHNIQUE_VOCABULARY",
    "CompletenessResult",
    "ReconstructionQuery",
    "ReconstructionResult",
    "SearchMetrics",
    "check_disambiguation",
    "compute_completeness",
    "find_shared_technique_terms",
    "reconstruct",
    "reconstruction_payload",
]
