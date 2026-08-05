"""EXP-HEKB006's Cross-Model Comparison Engine.

Given two real `_semantic_closure.SemanticClosure` values -- each already
computed by `_semantic_closure.compute_closure` (EXP-HEKB002, reused here
unmodified, exactly as EXP-HEKB003/004/005 already established) from a
real `hekb.category.KnowledgeCategory` that some observer's structural
output was ingested into -- this module computes purely structural
agreement metrics between them. It adds **no new retrieval algorithm**:
every function below is a comparison over an already-computed closure's
`objects`/`morphisms`/`pullback_roots`/`pushout_wavefront`, or over a
separately supplied `proof_path`. No vector or embedding search anywhere.

**Honest scope of each metric**, per specification section III:

- `closure_structure_similarity` (S_closure_sim) -- a real Jaccard
  similarity over (object id, typed morphism triple) sets. A real,
  computable quantity for any two closures, independent of whether real
  multi-LLM data produced them.
- `morphism_graph_edit_distance` (GED_morphism) -- a real, normalized
  structural edit-distance **proxy**: symmetric-difference cost over
  object and morphism sets, normalized by union size. This is a chosen,
  documented approximation (like EXP-HEKB003's `Depth_category` ordinal
  table), not a minimum-cost graph-isomorphism search (NP-hard in
  general, and not needed to detect real structural divergence between
  two closures).
- `pullback_pushout_identity_rate` (R_limit_identity) -- Jaccard
  similarity of `pullback_roots` and of `pushout_wavefront`, averaged.
- `proof_path_alignment` (P_proof_align) -- a real normalized
  longest-common-subsequence length between two `proof_path` sequences.
- `invariant_identity` (I_cross_model) -- requires two real
  `InvariantSignature.homotopy_hash`/`betti_numbers` values.
  `cle.homotopy` (categorical-lift-engine) is still Protocol-only -- the
  same gap EXP-HEKB002-005 already recorded -- so neither signature has
  ever been computed by anything in this workspace. This function returns
  `None` (the honest NOT-MEASURED result) whenever either side is `None`,
  and only computes a real boolean equality once both sides actually
  carry a real hash.
- `completeness_variance`/`latency_variance_ms` (Var(C_obs), tau_variance)
  -- a real population variance over per-observer values, `None` when
  fewer than 2 real values exist (variance across models is undefined for
  0 or 1 models -- never reported as `0.0`, which would misleadingly
  imply confirmed agreement).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, runtime_checkable

from _semantic_closure import SemanticClosure


@runtime_checkable
class InvariantSignatureLike(Protocol):
    """The `InvariantSignature` shape this module reads -- structural, so
    either `_observation_bundle.InvariantSignature` or
    `_visual_observation_bundle.InvariantSignature` (or any future
    corpus's own copy of the same shape) satisfies it without this module
    importing either concrete class."""

    @property
    def homotopy_hash(self) -> str | None: ...

    @property
    def betti_numbers(self) -> tuple[int, ...] | None: ...


def _morphism_triples(closure: SemanticClosure) -> frozenset[tuple[str, str, str]]:
    return frozenset((m.source, m.target, m.kind) for m in closure.morphisms)


def _object_ids(closure: SemanticClosure) -> frozenset[str]:
    return frozenset(obj.id for obj in closure.objects)


def _jaccard(a: frozenset[str], b: frozenset[str]) -> float:
    union = a | b
    if not union:
        return 1.0  # both empty: vacuously identical
    return len(a & b) / len(union)


def closure_structure_similarity(a: SemanticClosure, b: SemanticClosure) -> float:
    """S_closure_sim: Jaccard similarity of (objects union typed morphisms)
    between two real closures. `1.0` only when both the object set and the
    typed-morphism-triple set are identical."""
    objects_a, objects_b = _object_ids(a), _object_ids(b)
    morphisms_a, morphisms_b = _morphism_triples(a), _morphism_triples(b)
    union_size = len(objects_a | objects_b) + len(morphisms_a | morphisms_b)
    if union_size == 0:
        return 1.0
    intersection_size = len(objects_a & objects_b) + len(morphisms_a & morphisms_b)
    return intersection_size / union_size


def morphism_graph_edit_distance(a: SemanticClosure, b: SemanticClosure) -> float:
    """GED_morphism: a real, normalized structural edit-distance proxy --
    `1 - closure_structure_similarity`. `0.0` for structurally identical
    closures, approaching `1.0` as they share nothing. Documented as a
    symmetric-difference-based approximation, not a minimum graph-edit
    search; see module docstring."""
    return 1.0 - closure_structure_similarity(a, b)


def pullback_pushout_identity_rate(a: SemanticClosure, b: SemanticClosure) -> float:
    """R_limit_identity: mean of the Jaccard similarity of `pullback_roots`
    and of `pushout_wavefront` between two real closures."""
    pullback_similarity = _jaccard(frozenset(a.pullback_roots), frozenset(b.pullback_roots))
    pushout_similarity = _jaccard(frozenset(a.pushout_wavefront), frozenset(b.pushout_wavefront))
    return (pullback_similarity + pushout_similarity) / 2.0


def _lcs_length(a: tuple[str, ...], b: tuple[str, ...]) -> int:
    """A real, textbook dynamic-programming longest-common-subsequence
    length -- exact, not approximated."""
    previous = [0] * (len(b) + 1)
    for item_a in a:
        current = [0] * (len(b) + 1)
        for j, item_b in enumerate(b, start=1):
            current[j] = (
                previous[j - 1] + 1 if item_a == item_b else max(previous[j], current[j - 1])
            )
        previous = current
    return previous[-1]


def proof_path_alignment(a: tuple[str, ...], b: tuple[str, ...]) -> float:
    """P_proof_align: real normalized LCS length between two proof paths.
    `1.0` when one path's sequence of steps is fully preserved as a
    subsequence of the other; `0.0` when they share no ordered step at
    all. Two empty paths are vacuously aligned (`1.0`)."""
    longest = max(len(a), len(b))
    if longest == 0:
        return 1.0
    return _lcs_length(a, b) / longest


def invariant_identity(
    a: InvariantSignatureLike | None, b: InvariantSignatureLike | None
) -> bool | None:
    """I_cross_model: `None` (NOT MEASURED) whenever either side has no
    real `homotopy_hash` -- true for every signature in this workspace
    today, since `cle.homotopy` is Protocol-only. Only computes a real
    equality once both sides actually carry a real hash."""
    if a is None or b is None or a.homotopy_hash is None or b.homotopy_hash is None:
        return None
    return a.homotopy_hash == b.homotopy_hash and a.betti_numbers == b.betti_numbers


def _population_variance(values: tuple[float, ...]) -> float | None:
    if len(values) < 2:
        return None
    mean = sum(values) / len(values)
    return sum((v - mean) ** 2 for v in values) / len(values)


def completeness_variance(per_observer_completeness: tuple[float, ...]) -> float | None:
    """Var(C_obs): `None` when fewer than 2 real observer completeness
    values exist -- variance across models is undefined for 0 or 1
    models, and reporting `0.0` would misleadingly imply confirmed
    cross-model agreement that was never measured."""
    return _population_variance(per_observer_completeness)


def latency_variance_ms(per_observer_latency_ms: tuple[float, ...]) -> float | None:
    """tau_variance: same honesty rule as `completeness_variance`."""
    return _population_variance(per_observer_latency_ms)


@dataclass(frozen=True, slots=True)
class CrossModelComparison:
    """Every metric this module can compute for one pair of real,
    per-observer closures -- `invariant_identity` alone may be `None`."""

    observer_a: str
    observer_b: str
    closure_structure_similarity: float
    morphism_graph_edit_distance: float
    pullback_pushout_identity_rate: float
    proof_path_alignment: float
    invariant_identity: bool | None


def compare(
    observer_a: str,
    closure_a: SemanticClosure,
    proof_path_a: tuple[str, ...],
    signature_a: InvariantSignatureLike | None,
    observer_b: str,
    closure_b: SemanticClosure,
    proof_path_b: tuple[str, ...],
    signature_b: InvariantSignatureLike | None,
) -> CrossModelComparison:
    """Every real metric this module can compute for one observer pair."""
    return CrossModelComparison(
        observer_a=observer_a,
        observer_b=observer_b,
        closure_structure_similarity=closure_structure_similarity(closure_a, closure_b),
        morphism_graph_edit_distance=morphism_graph_edit_distance(closure_a, closure_b),
        pullback_pushout_identity_rate=pullback_pushout_identity_rate(closure_a, closure_b),
        proof_path_alignment=proof_path_alignment(proof_path_a, proof_path_b),
        invariant_identity=invariant_identity(signature_a, signature_b),
    )


__all__ = [
    "CrossModelComparison",
    "InvariantSignatureLike",
    "closure_structure_similarity",
    "compare",
    "completeness_variance",
    "invariant_identity",
    "latency_variance_ms",
    "morphism_graph_edit_distance",
    "proof_path_alignment",
    "pullback_pushout_identity_rate",
]
