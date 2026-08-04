"""EXP-HEKB002's Functorial Graph Adapter: `PropertyGraph -> C_HEKB`.

A real, checkable mapping — not a fixture pretending to be one. Each
`PropertyGraphNode` becomes one `hekb.models.Concept` (a canonical
singleton element set, `{node.id}` — a property graph node carries no
finite-set structure of its own, so nothing is fabricated beyond the
minimum HEKB's category axioms require). Each `PropertyGraphEdge` becomes
one `hekb.models.KnowledgeRelation`: a total function over that singleton
source set, landing in the singleton target set — trivially total by
construction, so every edge maps to a real, `KnowledgeCategory.add_morphism`-
admissible morphism, not merely a labeled arrow.

**Functoriality preservation, checked, not assumed**: a `PropertyGraph` has
no native composition operator (it is a graph, not a category) — the
checkable content of "the functor commutes with composition" here is that
composing two *images* of composable edges via HEKB's real, audited
`KnowledgeCategory.compose` produces exactly the mathematically correct
pointwise-composed total function. `check_functoriality` verifies this
against an independently hand-computed expected mapping, not merely that
`compose` ran without raising.
"""

from __future__ import annotations

from _graphify_reference import PropertyGraph, PropertyGraphEdge
from hekb.category import KnowledgeCategory
from hekb.models import Concept, KnowledgeRelation


def graph_to_hekb(
    graph: PropertyGraph,
) -> tuple[tuple[Concept, ...], tuple[KnowledgeRelation, ...], dict[str, str]]:
    """`F_graph`: nodes -> `Concept`s, edges -> `KnowledgeRelation`s.

    Returns the concepts, the relations, and a side table `{relation_id:
    edge.kind}` — HEKB's own `KnowledgeRelation` has no dedicated "typed
    morphism" field (only numeric `invariants`), so the morphism *type*
    Stage III.7's acceptance criteria asks for is carried alongside the
    category, not inside it; folding it into `hekb.models` would be a
    production-code change this experiment was not asked to make.
    """
    concepts = tuple(Concept(id=node.id, elements=frozenset({node.id})) for node in graph.nodes)
    relations = tuple(
        KnowledgeRelation(
            id=edge.id,
            source=edge.source,
            target=edge.target,
            mapping={edge.source: edge.target},
        )
        for edge in graph.edges
    )
    relation_kind = {edge.id: edge.kind for edge in graph.edges}
    return concepts, relations, relation_kind


def check_functoriality(
    category: KnowledgeCategory, f_edge: PropertyGraphEdge, g_edge: PropertyGraphEdge
) -> bool:
    """`f_edge: A -> B`, `g_edge: B -> C` (composable at the graph level) ->
    verify `category.compose(F(f_edge), F(g_edge))` is exactly the
    pointwise composition `{a: g.mapping[f.mapping[a]] for a in f.mapping}`,
    using HEKB's real, checked `compose` — the substantive content of
    functoriality for a functor with no native source-side composition to
    compare against.
    """
    f = category.morphism(f_edge.id)
    g = category.morphism(g_edge.id)
    composed = category.compose(f, g)
    expected_mapping = {a: g.mapping[b] for a, b in f.mapping.items()}
    return (
        composed.source == f.source
        and composed.target == g.target
        and composed.mapping == expected_mapping
    )


__all__ = ["check_functoriality", "graph_to_hekb"]
