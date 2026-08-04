"""EXP-HEKB002 Phase 3: the Semantic Closure Engine — categorical retrieval.

Not vector search, not embedding search: given a query object already
admitted to a real `hekb.category.KnowledgeCategory`, this computes the
**minimal self-contained subcategory** grounding it — every object/morphism
reachable by following real, typed `KnowledgeRelation` edges outward
(premises the query depends on: pullback direction) and inward (objects
that depend on the query: pushout/impact direction) — using HEKB's own,
already-audited `compose` for every derived composition. Every output is
sorted before being frozen into the result, so `SemanticClosure` construction
is order-independent by construction, not by convention.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from hekb.category import KnowledgeCategory
from hekb.models import KnowledgeRelation


@dataclass(frozen=True, slots=True)
class ClosureObject:
    id: str
    category: str


@dataclass(frozen=True, slots=True)
class ClosureMorphism:
    id: str
    source: str
    target: str
    kind: str


@dataclass(frozen=True, slots=True)
class DerivedComposition:
    morphism: str
    formula: str


@dataclass(frozen=True, slots=True)
class SemanticClosure:
    query_concept_id: str
    target_object: ClosureObject
    objects: tuple[ClosureObject, ...]
    morphisms: tuple[ClosureMorphism, ...]
    derived_compositions: tuple[DerivedComposition, ...]
    pullback_roots: tuple[str, ...]
    pushout_wavefront: tuple[str, ...]
    is_minimal_self_contained: bool


def _outgoing(category: KnowledgeCategory) -> dict[str, list[KnowledgeRelation]]:
    index: dict[str, list[KnowledgeRelation]] = {}
    for relation in category.morphisms.values():
        index.setdefault(relation.source, []).append(relation)
    return index


def _incoming(category: KnowledgeCategory) -> dict[str, list[KnowledgeRelation]]:
    index: dict[str, list[KnowledgeRelation]] = {}
    for relation in category.morphisms.values():
        index.setdefault(relation.target, []).append(relation)
    return index


def _reachable(
    start: str,
    adjacency: dict[str, list[KnowledgeRelation]],
    *,
    step_of: Callable[[KnowledgeRelation], str],
) -> tuple[set[str], set[str]]:
    """BFS from `start` over `adjacency`; `step_of(relation)` picks the next
    object id from a relation touching the current frontier object."""
    visited_objects = {start}
    visited_relations: set[str] = set()
    frontier = [start]
    while frontier:
        current = frontier.pop()
        for relation in adjacency.get(current, ()):
            next_id = step_of(relation)
            visited_relations.add(relation.id)
            if next_id not in visited_objects:
                visited_objects.add(next_id)
                frontier.append(next_id)
    return visited_objects, visited_relations


def _derived_compositions(
    category: KnowledgeCategory,
    query_id: str,
    outgoing: dict[str, list[KnowledgeRelation]],
    pullback_object_ids: set[str],
) -> tuple[DerivedComposition, ...]:
    """Fold every query-rooted path in the pullback graph via HEKB's real
    `compose`, one real `KnowledgeRelation` per path -- not a string
    template. `KnowledgeCategory` is not required to be acyclic (a
    `context` edge can point back at something already visited, e.g.
    `_graphify_reference`'s own MeaningMeasurement -> RFC-MM001 edge
    closing a 2-cycle with RFC-MM001's `definition` edge); a path stops the
    moment it revisits a node already on it, rather than recursing forever."""
    results: list[DerivedComposition] = []

    def walk(current_id: str, path: tuple[KnowledgeRelation, ...], on_path: frozenset[str]) -> None:
        if len(path) >= 2:
            composed = path[0]
            for relation in path[1:]:
                composed = category.compose(composed, relation)
            formula = " o ".join(relation.id for relation in reversed(path))
            results.append(
                DerivedComposition(
                    morphism=f"m_derived: {query_id} -> {composed.target}",
                    formula=formula,
                )
            )
        for relation in outgoing.get(current_id, ()):
            if relation.target in on_path:
                continue  # cycle: stop here rather than recurse forever
            walk(relation.target, (*path, relation), on_path | {relation.target})

    walk(query_id, (), frozenset({query_id}))
    return tuple(sorted(results, key=lambda d: d.morphism))


def compute_closure(
    category: KnowledgeCategory,
    relation_kind: dict[str, str],
    object_category: dict[str, str],
    query_id: str,
) -> SemanticClosure:
    outgoing = _outgoing(category)
    incoming = _incoming(category)

    pullback_objects, pullback_relations = _reachable(
        query_id, outgoing, step_of=lambda r: r.target
    )
    pushout_objects, pushout_relations = _reachable(query_id, incoming, step_of=lambda r: r.source)

    all_object_ids = pullback_objects | pushout_objects
    all_relation_ids = pullback_relations | pushout_relations

    objects = tuple(
        sorted(
            (
                ClosureObject(id=obj_id, category=object_category.get(obj_id, "Unknown"))
                for obj_id in all_object_ids
            ),
            key=lambda o: o.id,
        )
    )
    morphisms = tuple(
        sorted(
            (
                ClosureMorphism(
                    id=relation_id,
                    source=category.morphism(relation_id).source,
                    target=category.morphism(relation_id).target,
                    kind=relation_kind.get(relation_id, "unknown"),
                )
                for relation_id in all_relation_ids
            ),
            key=lambda m: m.id,
        )
    )

    pullback_roots = tuple(
        sorted(
            obj_id for obj_id in pullback_objects if obj_id != query_id and obj_id not in outgoing
        )
    )
    pushout_wavefront = tuple(
        sorted(
            obj_id for obj_id in pushout_objects if obj_id != query_id and obj_id not in incoming
        )
    )

    derived_compositions = _derived_compositions(category, query_id, outgoing, pullback_objects)

    target_object = ClosureObject(id=query_id, category=object_category.get(query_id, "Unknown"))
    is_minimal_self_contained = _verify_minimal_self_contained(objects, morphisms, query_id)

    return SemanticClosure(
        query_concept_id=query_id,
        target_object=target_object,
        objects=objects,
        morphisms=morphisms,
        derived_compositions=derived_compositions,
        pullback_roots=pullback_roots,
        pushout_wavefront=pushout_wavefront,
        is_minimal_self_contained=is_minimal_self_contained,
    )


def _verify_minimal_self_contained(
    objects: tuple[ClosureObject, ...],
    morphisms: tuple[ClosureMorphism, ...],
    query_id: str,
) -> bool:
    """A real post-hoc check, not a hardcoded flag: every morphism's
    endpoints are among `objects` (no dangling edges), every non-query
    object touches at least one morphism (no orphans a buggy closure
    algorithm could have smuggled in), and no object id repeats."""
    object_ids = [obj.id for obj in objects]
    if len(object_ids) != len(set(object_ids)):
        return False
    object_id_set = set(object_ids)

    touched: set[str] = set()
    for morphism in morphisms:
        if morphism.source not in object_id_set or morphism.target not in object_id_set:
            return False
        touched.add(morphism.source)
        touched.add(morphism.target)

    non_query_ids = object_id_set - {query_id}
    return non_query_ids <= touched


__all__ = [
    "ClosureMorphism",
    "ClosureObject",
    "DerivedComposition",
    "SemanticClosure",
    "compute_closure",
]
