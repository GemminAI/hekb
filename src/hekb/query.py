"""Query — HEKB's read side: nearest-neighbour and shortest-path over K.

Reuses the same :class:`~hekb.category.KnowledgeCategory` :mod:`hekb.runtime`
already writes into — this is not a second, competing store. Distance is
plain Euclidean over ``Concept.centroid``: the same "carry the payload
through, never interpret it" discipline :mod:`hekb.models` already
documents applied to distance too — generic numeric comparison of an
opaque payload, not a physics-aware metric. A manifold-aware, physics-informed
distance stays NVS-Kernel's concern; HEKB does not import it.

Algorithm shape (exhaustive nearest-neighbour with a deterministic
tie-break, Dijkstra over non-negative edge costs) is carried over from
NVS-Kernel's ``nvs_kernel.hekb``/``nvs_kernel.memory`` reference
implementation, adapted to query ``KnowledgeCategory`` directly instead of
a second in-memory graph.
"""

from __future__ import annotations

import heapq
import math
from dataclasses import dataclass

from hekb.category import KnowledgeCategory
from hekb.models import Concept, KnowledgeRelation


@dataclass(frozen=True, slots=True)
class QueryHit:
    concept: Concept
    distance: float


@dataclass(frozen=True, slots=True)
class GeodesicPath:
    concept_ids: tuple[str, ...]
    total_cost: float
    reachable: bool


def _euclidean_distance(a: tuple[float, ...], b: tuple[float, ...]) -> float:
    if len(a) != len(b):
        raise ValueError(f"centroid dimension mismatch: {len(a)} != {len(b)}")
    return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b, strict=True)))


def nearest(
    category: KnowledgeCategory, position: tuple[float, ...], count: int
) -> tuple[QueryHit, ...]:
    """The `count` closest concepts to `position`, by Euclidean centroid distance.

    Concepts with no centroid are excluded — there is nothing to compare.
    """
    if count < 1:
        raise ValueError("count must be positive")
    hits: list[QueryHit] = []
    for concept in category.objects.values():
        if concept.centroid is None:
            continue
        hits.append(
            QueryHit(concept=concept, distance=_euclidean_distance(position, concept.centroid))
        )
    hits.sort(key=lambda hit: (hit.distance, hit.concept.id))
    return tuple(hits[:count])


def neighbours(category: KnowledgeCategory, concept_id: str) -> tuple[KnowledgeRelation, ...]:
    """Every morphism with `concept_id` as its source, cheapest first.

    Raises ``KeyError`` for an unknown `concept_id`, the same convention
    :meth:`KnowledgeCategory.object` already uses.
    """
    category.object(concept_id)
    edges = [
        relation for relation in category.morphisms.values() if relation.source == concept_id
    ]
    edges.sort(key=lambda edge: (edge.cost, edge.target))
    return tuple(edges)


def geodesic(category: KnowledgeCategory, source_id: str, target_id: str) -> GeodesicPath:
    """Minimum-cost morphism path `source_id -> target_id`.

    Dijkstra, since every ``KnowledgeRelation.cost`` is non-negative
    (enforced in ``KnowledgeRelation.__post_init__``). An unreachable pair
    is reported as unreachable rather than as an infinite-cost path.
    """
    category.object(source_id)
    category.object(target_id)
    if source_id == target_id:
        return GeodesicPath((source_id,), 0.0, True)

    adjacency: dict[str, list[KnowledgeRelation]] = {}
    for relation in category.morphisms.values():
        adjacency.setdefault(relation.source, []).append(relation)

    distances: dict[str, float] = {source_id: 0.0}
    previous: dict[str, str] = {}
    queue: list[tuple[float, str]] = [(0.0, source_id)]
    visited: set[str] = set()

    while queue:
        cost, current = heapq.heappop(queue)
        if current in visited:
            continue
        visited.add(current)
        if current == target_id:
            break
        for edge in sorted(adjacency.get(current, ()), key=lambda item: (item.cost, item.target)):
            candidate = cost + edge.cost
            if candidate < distances.get(edge.target, float("inf")):
                distances[edge.target] = candidate
                previous[edge.target] = current
                heapq.heappush(queue, (candidate, edge.target))

    if target_id not in distances:
        return GeodesicPath((), float("inf"), False)

    path = [target_id]
    while path[-1] != source_id:
        path.append(previous[path[-1]])
    path.reverse()
    return GeodesicPath(tuple(path), distances[target_id], True)


__all__ = ["GeodesicPath", "QueryHit", "geodesic", "nearest", "neighbours"]
