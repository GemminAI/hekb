"""EXP-HEKB006 v2.1.0's Reality Consensus Engine.

The specification's Reality Consensus Engine is defined as a **pullback
limit over typed morphisms** -- not majority voting, not an LLM judge, not
a new retrieval algorithm:

    S_consensus(Q) = lim_k S(Q)^(M_k)
                   = ( Q_nodes, intersection_k Mor(S(Q)^(M_k)), S(Q)_pullback )

Every function in this module operates purely on already-computed
`_semantic_closure.SemanticClosure` values (EXP-HEKB002, reused unmodified
here as everywhere else in this experiment series) -- the same real
object-id and typed-morphism-triple sets `_cross_model_compare.py` already
established as the honest unit of structural comparison. This module
generalizes that pairwise machinery to K >= 1 observers of the *same*
target object; it adds no vector or embedding search, and no new graph
traversal (closures are already computed elsewhere; this module only does
set arithmetic over their `objects`/`morphisms`).

**What each function honestly measures**:

- `compute_reality_consensus` -- the Pullback Limit itself: the
  intersection of every observer's (object-id, typed-morphism-triple)
  sets is the "signal" every observer agrees on; the union is what
  *any* observer contributed. `consensus_reality_score` (R_consensus,
  specification section IV.4) is the ratio of the two -- 1.0 only when
  every observer's closure is identical.
- `observer_bias_index` (OBI, section IV.3) -- what fraction of one
  observer's own closure lies *outside* the agreed intersection core.
  `0.0` means this observer's entire closure is already part of the
  consensus core (no idiosyncratic content); it rises toward `1.0` as
  more of the observer's content is unique to it.
- `leave_one_out_robustness` (Rob_observer, section IV.5) -- Jaccard
  agreement between the full-K consensus core and the consensus core
  recomputed with one observer removed. A single observer's `Rob` value
  measures whether the *other* K-1 observers alone reconstruct the same
  core; it says nothing about that observer's own bias (see
  `observer_bias_index` for that).
- `false_convergence_check` (F_convergence, section IV.6) -- whether two
  *different* real target objects' consensus object sets improperly
  overlap outside deliberately shared structural nodes (e.g. a real
  cross-work technique node every observer of both works independently
  found) -- the same check `_visual_reconstruction.check_disambiguation`
  already performs pairwise, generalized to consensus level.

A consensus computed from a single observer (K=1) is degenerate --
intersection equals union equals that one observer's own closure, so
`consensus_reality_score` is vacuously `1.0`. This is documented, not
hidden: `compute_reality_consensus` requires `require_min_observers` (default
2) unless explicitly overridden, so a caller cannot silently mistake "one
observer, trivially agreeing with itself" for real multi-observer
consensus.
"""

from __future__ import annotations

from dataclasses import dataclass

from _semantic_closure import SemanticClosure

MorphismTriple = tuple[str, str, str]  # (source, target, kind)


class InsufficientObserversError(ValueError):
    """Raised when a consensus operation is asked to run below its
    documented minimum observer count -- never silently degraded."""


@dataclass(frozen=True, slots=True)
class ObserverClosure:
    """One real observer's already-computed closure of a shared target.
    `observer` is a label only -- see `anonymize` below for the Blind
    Observer Independence check (Test F), which verifies no consensus
    computation actually depends on this field's value."""

    observer: str
    closure: SemanticClosure


def _triples(closure: SemanticClosure) -> frozenset[MorphismTriple]:
    return frozenset((m.source, m.target, m.kind) for m in closure.morphisms)


def _object_ids(closure: SemanticClosure) -> frozenset[str]:
    return frozenset(o.id for o in closure.objects)


@dataclass(frozen=True, slots=True)
class RealityConsensusResult:
    """The Pullback Limit S_consensus(Q) for one target, over K observers."""

    target_id: str
    participating_observers: tuple[str, ...]
    intersection_object_ids: tuple[str, ...]
    union_object_ids: tuple[str, ...]
    intersection_morphism_triples: tuple[MorphismTriple, ...]
    union_morphism_triples: tuple[MorphismTriple, ...]
    consensus_reality_score: float


def compute_reality_consensus(
    target_id: str,
    observers: tuple[ObserverClosure, ...],
    *,
    require_min_observers: int = 2,
) -> RealityConsensusResult:
    """R_consensus (specification section IV.4): the Pullback Limit over
    `observers`' already-computed closures of the same real `target_id`.
    Raises `InsufficientObserversError` below `require_min_observers` --
    pass `require_min_observers=1` explicitly to permit the degenerate,
    vacuously-1.0 single-observer case (e.g. for a mechanism smoke test),
    never as a silent default."""
    if len(observers) < require_min_observers:
        raise InsufficientObserversError(
            f"compute_reality_consensus for {target_id!r} requires >= "
            f"{require_min_observers} observers, got {len(observers)}"
        )

    object_sets = [_object_ids(oc.closure) for oc in observers]
    triple_sets = [_triples(oc.closure) for oc in observers]

    intersection_objects = frozenset.intersection(*object_sets)
    union_objects = frozenset.union(*object_sets)
    intersection_triples = frozenset.intersection(*triple_sets)
    union_triples = frozenset.union(*triple_sets)

    union_size = len(union_objects) + len(union_triples)
    intersection_size = len(intersection_objects) + len(intersection_triples)
    score = intersection_size / union_size if union_size else 1.0

    return RealityConsensusResult(
        target_id=target_id,
        participating_observers=tuple(oc.observer for oc in observers),
        intersection_object_ids=tuple(sorted(intersection_objects)),
        union_object_ids=tuple(sorted(union_objects)),
        intersection_morphism_triples=tuple(sorted(intersection_triples)),
        union_morphism_triples=tuple(sorted(union_triples)),
        consensus_reality_score=score,
    )


def observer_bias_index(
    observer_closure: ObserverClosure, consensus: RealityConsensusResult
) -> float:
    """OBI(M_k) (specification section IV.3): the fraction of
    `observer_closure`'s own (objects + typed-morphism-triples) that lies
    outside `consensus`'s intersection core. `0.0` for an observer whose
    entire closure is already agreed upon by every other observer; `1.0`
    only for an observer sharing nothing with the core."""
    own_objects = _object_ids(observer_closure.closure)
    own_triples = _triples(observer_closure.closure)
    own_size = len(own_objects) + len(own_triples)
    if own_size == 0:
        return 0.0
    core_objects = frozenset(consensus.intersection_object_ids)
    core_triples = frozenset(consensus.intersection_morphism_triples)
    shared_size = len(own_objects & core_objects) + len(own_triples & core_triples)
    return 1.0 - (shared_size / own_size)


def leave_one_out_robustness(
    target_id: str, observers: tuple[ObserverClosure, ...]
) -> dict[str, float]:
    """Rob_observer(M_j) (specification section IV.5) for every observer in
    `observers`: Jaccard agreement between the full-K consensus core and
    the core recomputed with M_j held out. Requires >= 3 observers (>= 2
    remain after holding one out, so the reduced consensus is itself a
    real multi-observer consensus, not a single closure vacuously equal to
    itself)."""
    if len(observers) < 3:
        raise InsufficientObserversError(
            f"leave_one_out_robustness for {target_id!r} requires >= 3 observers "
            f"so >= 2 remain after holding one out, got {len(observers)}"
        )
    full = compute_reality_consensus(target_id, observers)
    full_objects = frozenset(full.intersection_object_ids)
    full_triples = frozenset(full.intersection_morphism_triples)

    results: dict[str, float] = {}
    for i, excluded in enumerate(observers):
        remaining = observers[:i] + observers[i + 1 :]
        reduced = compute_reality_consensus(target_id, remaining)
        reduced_objects = frozenset(reduced.intersection_object_ids)
        reduced_triples = frozenset(reduced.intersection_morphism_triples)
        union_size = len(full_objects | reduced_objects) + len(full_triples | reduced_triples)
        intersection_size = len(full_objects & reduced_objects) + len(
            full_triples & reduced_triples
        )
        results[excluded.observer] = intersection_size / union_size if union_size else 1.0
    return results


@dataclass(frozen=True, slots=True)
class FalseConvergenceResult:
    target_a: str
    target_b: str
    non_structural_overlap_ids: tuple[str, ...]
    false_convergence_rate: float
    disambiguated: bool


def false_convergence_check(
    consensus_a: RealityConsensusResult,
    consensus_b: RealityConsensusResult,
    *,
    shared_structural_ids: frozenset[str] = frozenset(),
) -> FalseConvergenceResult:
    """F_convergence (specification section IV.6): two *different* real
    target objects' consensus object sets must not overlap except at
    `shared_structural_ids` -- real, independently-verified shared nodes
    (e.g. a cross-work technique node every observer of both works found
    in real text; see `_visual_reconstruction.find_shared_technique_terms`).
    Any other overlap is a real false merge, not a legitimate invariant."""
    ids_a = frozenset(consensus_a.union_object_ids)
    ids_b = frozenset(consensus_b.union_object_ids)
    overlap = sorted((ids_a & ids_b) - shared_structural_ids)
    smaller = min(len(ids_a), len(ids_b))
    rate = len(overlap) / smaller if smaller else 0.0
    return FalseConvergenceResult(
        target_a=consensus_a.target_id,
        target_b=consensus_b.target_id,
        non_structural_overlap_ids=tuple(overlap),
        false_convergence_rate=rate,
        disambiguated=len(overlap) == 0,
    )


def anonymize(observers: tuple[ObserverClosure, ...]) -> tuple[ObserverClosure, ...]:
    """Test F (Blind Observer Independence): replace every real observer
    label with an anonymous `Observer_N` token, preserving closure content
    unchanged. `compute_reality_consensus` on the result must be numerically
    identical to the original (aside from `participating_observers`'
    labels) -- consensus arithmetic reads only `closure.objects`/
    `closure.morphisms`, never `observer`, so this is a real, checkable
    property, not an assumption."""
    return tuple(
        ObserverClosure(observer=f"Observer_{i + 1}", closure=oc.closure)
        for i, oc in enumerate(observers)
    )


__all__ = [
    "FalseConvergenceResult",
    "InsufficientObserversError",
    "MorphismTriple",
    "ObserverClosure",
    "RealityConsensusResult",
    "anonymize",
    "compute_reality_consensus",
    "false_convergence_check",
    "leave_one_out_robustness",
    "observer_bias_index",
]
