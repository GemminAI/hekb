"""EXP-HEKB003 Stage 4: a reference Semantic Search layer over HEKB.

Concept Resolution -> Typed Object Lookup -> Semantic Closure -> Pullback ->
Pushout -> Minimal Self-Contained Subcategory -> ranked payload. Pure
categorical retrieval, built entirely on `_semantic_closure.compute_closure`
(no redesign of the closure algorithm itself) plus a geometric ranking
function over its result. **Not vector search, not embedding search**: no
step here computes or compares a learned embedding; every distance below
is either a real graph-theoretic quantity (hop counts over real typed
morphisms) or a real geometric quantity already carried by `hekb.models.Concept`
(`centroid`, when a caller populated it — see EXP-HEKB002's `_cle_hekb_adapter`).

## The geometric ranking function

EXP-HEKB003 §II.2 specifies
`D_ranking = w1*D_functorial + w2*L_morphism + w3*D_potential + w4*Depth_category`.
Each term, made concrete and honest about what it can and cannot measure at
this stage:

- `L_morphism`: real shortest-path hop count from the query to the
  candidate, over the closure's morphisms treated as **undirected** (a
  premise or an impact both count as "one step of relatedness").
- `D_functorial`: real shortest-path hop count over the closure's morphisms
  restricted to the **pullback (premise) direction only** — a distinct,
  real quantity from `L_morphism`, not a relabeling of it.
- `D_potential`: a real Mahalanobis-style distance between two objects'
  `centroid`s, when *both* carry one (today, only CLE-derived concepts
  do — see EXP-HEKB002). `0.0`, honestly, when unavailable — never a
  fabricated placeholder.
- `Depth_category`: a fixed, documented ordinal table by object category
  (below) — a real, if simple, abstraction-depth proxy, not derived from
  any learned signal.

All four terms are normalized to `[0, 1]` before weighting so no single
term dominates by construction of its own units.
"""

from __future__ import annotations

import math
import time
from dataclasses import dataclass
from typing import Any

from _semantic_closure import SemanticClosure, compute_closure
from hekb.category import KnowledgeCategory
from hekb.models import Concept

#: Lower = more concrete/closer to the source of truth; higher = more abstract.
CATEGORY_DEPTH = {
    "DomainConcept": 0,
    "CrystallizedKnowledge": 0,
    "CodeImplementation": 1,
    "SpecificationDocument": 2,
    "GitCommit": 3,
}
_MAX_CATEGORY_DEPTH = max(CATEGORY_DEPTH.values())

DEFAULT_WEIGHTS = (0.4, 0.3, 0.2, 0.1)  # w1..w4, documented choice, not derived


@dataclass(frozen=True, slots=True)
class RankedObject:
    id: str
    category: str
    score: float
    d_functorial: float
    l_morphism: float
    d_potential: float
    depth_category: float


@dataclass(frozen=True, slots=True)
class SearchResult:
    raw_term: str
    resolved_concept_id: str
    closure: SemanticClosure
    ranked_objects: tuple[RankedObject, ...]
    proof_path: tuple[str, ...]
    context_economy_ratio: float
    false_inclusion_rate: float
    execution_time_ms: float


def resolve_concept(raw_term: str, category: KnowledgeCategory) -> str | None:
    """Exact, then case-insensitive, id match against real objects already
    admitted to the category. No fuzzy/NLP matching -- categorical
    retrieval resolves to a real object or it doesn't."""
    if raw_term in category.objects:
        return raw_term
    lowered = raw_term.lower()
    for object_id in category.objects:
        if object_id.lower() == lowered:
            return object_id
    return None


def _undirected_adjacency(closure: SemanticClosure) -> dict[str, set[str]]:
    adjacency: dict[str, set[str]] = {}
    for morphism in closure.morphisms:
        adjacency.setdefault(morphism.source, set()).add(morphism.target)
        adjacency.setdefault(morphism.target, set()).add(morphism.source)
    return adjacency


def _directed_pullback_adjacency(closure: SemanticClosure) -> dict[str, set[str]]:
    adjacency: dict[str, set[str]] = {}
    for morphism in closure.morphisms:
        adjacency.setdefault(morphism.source, set()).add(morphism.target)
    return adjacency


def _bfs_hops(start: str, target: str, adjacency: dict[str, set[str]]) -> int | None:
    if start == target:
        return 0
    visited = {start}
    frontier = [start]
    hops = 0
    while frontier:
        hops += 1
        next_frontier: list[str] = []
        for node in frontier:
            for neighbor in adjacency.get(node, ()):
                if neighbor == target:
                    return hops
                if neighbor not in visited:
                    visited.add(neighbor)
                    next_frontier.append(neighbor)
        frontier = next_frontier
    return None


def _bfs_shortest_path(start: str, target: str, adjacency: dict[str, set[str]]) -> tuple[str, ...]:
    if start == target:
        return (start,)
    parents: dict[str, str] = {}
    visited = {start}
    frontier = [start]
    while frontier:
        next_frontier: list[str] = []
        for node in frontier:
            for neighbor in adjacency.get(node, ()):
                if neighbor in visited:
                    continue
                visited.add(neighbor)
                parents[neighbor] = node
                if neighbor == target:
                    path = [target]
                    while path[-1] != start:
                        path.append(parents[path[-1]])
                    return tuple(reversed(path))
                next_frontier.append(neighbor)
        frontier = next_frontier
    return ()


def _mahalanobis_like(a: Concept, b: Concept) -> float | None:
    if a.centroid is None or b.centroid is None or len(a.centroid) != len(b.centroid):
        return None
    return math.sqrt(sum((x - y) ** 2 for x, y in zip(a.centroid, b.centroid, strict=True)))


def _normalize_hops(hops: int | None, scale: int) -> float:
    if hops is None:
        return 1.0  # maximally distant: unreachable in this direction
    return hops / scale if scale > 0 else 0.0


def rank_objects(
    closure: SemanticClosure,
    category: KnowledgeCategory,
    weights: tuple[float, float, float, float] = DEFAULT_WEIGHTS,
) -> tuple[RankedObject, ...]:
    w1, w2, w3, w4 = weights
    undirected = _undirected_adjacency(closure)
    pullback_only = _directed_pullback_adjacency(closure)
    scale = max(len(closure.objects) - 1, 1)

    query_concept = category.objects.get(closure.query_concept_id)

    ranked = []
    for obj in closure.objects:
        l_morphism = _normalize_hops(_bfs_hops(closure.query_concept_id, obj.id, undirected), scale)
        d_functorial = _normalize_hops(
            _bfs_hops(closure.query_concept_id, obj.id, pullback_only), scale
        )

        d_potential = 0.0
        if query_concept is not None:
            candidate_concept = category.objects.get(obj.id)
            if candidate_concept is not None:
                distance = _mahalanobis_like(query_concept, candidate_concept)
                if distance is not None:
                    d_potential = distance / (1.0 + distance)  # squashed into [0, 1)

        depth_category = CATEGORY_DEPTH.get(obj.category, _MAX_CATEGORY_DEPTH) / max(
            _MAX_CATEGORY_DEPTH, 1
        )

        score = w1 * d_functorial + w2 * l_morphism + w3 * d_potential + w4 * depth_category
        ranked.append(
            RankedObject(
                id=obj.id,
                category=obj.category,
                score=score,
                d_functorial=d_functorial,
                l_morphism=l_morphism,
                d_potential=d_potential,
                depth_category=depth_category,
            )
        )
    return tuple(sorted(ranked, key=lambda r: (r.score, r.id)))


def _verify_no_false_inclusions(closure: SemanticClosure) -> float:
    """Independent re-verification, from scratch, that every closure object
    is actually reachable from the query via the closure's own morphisms
    (undirected) -- not merely trusted because the closure algorithm
    included it. Returns the false-inclusion rate, a real measured
    fraction, not an assumed constant."""
    adjacency = _undirected_adjacency(closure)
    unreachable = sum(
        1
        for obj in closure.objects
        if obj.id != closure.query_concept_id
        and _bfs_hops(closure.query_concept_id, obj.id, adjacency) is None
    )
    denominator = max(len(closure.objects) - 1, 1)
    return unreachable / denominator


def search(
    raw_term: str,
    category: KnowledgeCategory,
    relation_kind: dict[str, str],
    object_category: dict[str, str],
    weights: tuple[float, float, float, float] = DEFAULT_WEIGHTS,
) -> SearchResult | None:
    start = time.perf_counter()
    resolved = resolve_concept(raw_term, category)
    if resolved is None:
        return None

    closure = compute_closure(category, relation_kind, object_category, resolved)
    ranked = rank_objects(closure, category, weights)
    false_inclusion_rate = _verify_no_false_inclusions(closure)
    context_economy_ratio = len(closure.objects) / max(len(category.objects), 1)

    pullback_only = _directed_pullback_adjacency(closure)
    if closure.pullback_roots:
        deepest_root = max(
            closure.pullback_roots,
            key=lambda root_id: _bfs_hops(resolved, root_id, pullback_only) or 0,
        )
        proof_path = _bfs_shortest_path(resolved, deepest_root, pullback_only)
    else:
        proof_path = (resolved,)

    elapsed_ms = (time.perf_counter() - start) * 1000.0
    return SearchResult(
        raw_term=raw_term,
        resolved_concept_id=resolved,
        closure=closure,
        ranked_objects=ranked,
        proof_path=proof_path,
        context_economy_ratio=context_economy_ratio,
        false_inclusion_rate=false_inclusion_rate,
        execution_time_ms=elapsed_ms,
    )


def search_result_payload(result: SearchResult) -> dict[str, Any]:
    """EXP-HEKB003 §V-shaped response payload."""
    return {
        "query": {
            "raw_term": result.raw_term,
            "resolved_concept_id": result.resolved_concept_id,
        },
        "search_metrics": {
            "composition_depth": max(
                (dc.formula.count(" o ") + 1 for dc in result.closure.derived_compositions),
                default=0,
            ),
            "false_inclusion_rate": result.false_inclusion_rate,
            "context_economy_ratio": result.context_economy_ratio,
            "execution_time_ms": result.execution_time_ms,
        },
        "semantic_closure": {
            "target_object": {
                "id": result.closure.target_object.id,
                "category": result.closure.target_object.category,
            },
            "objects": [
                {"id": r.id, "category": r.category, "score": round(r.score, 6)}
                for r in result.ranked_objects
            ],
            "morphisms": [
                {"source": m.source, "target": m.target, "type": m.kind}
                for m in result.closure.morphisms
            ],
            "proof_path": list(result.proof_path),
            "pullback_roots": list(result.closure.pullback_roots),
            "pushout_wavefront": list(result.closure.pushout_wavefront),
        },
    }


__all__ = [
    "CATEGORY_DEPTH",
    "DEFAULT_WEIGHTS",
    "RankedObject",
    "SearchResult",
    "rank_objects",
    "resolve_concept",
    "search",
    "search_result_payload",
]
