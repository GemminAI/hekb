"""EXP-HEKB002 Path B's input: a deterministic property-graph fixture.

Not production Graphify. No Graphify repository exists anywhere in this
workspace (recorded in EXP-HEKB001's `docs/RFC_ALIGNMENT.md`, unchanged
since); this experiment does not invent a Markdown parser or a
`ProducerLike` interface to stand in for one — Graphify's real interface
is Graphify's own to define. This module is a **fixture**: a small,
hand-specified `PropertyGraph` value shaped the way Graphify's output is
*expected* to look (nodes + typed edges), extending EXP-HEKB001's
RFC-MM001/RFC-MSR01 example with the four morphism types EXP-HEKB002 §III.7
names (`definition`, `dependency`, `refinement`, `context`).
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class PropertyGraphNode:
    id: str
    category: str


@dataclass(frozen=True, slots=True)
class PropertyGraphEdge:
    id: str
    source: str
    target: str
    kind: str  # one of: "definition", "dependency", "refinement", "context"


@dataclass(frozen=True, slots=True)
class PropertyGraph:
    nodes: tuple[PropertyGraphNode, ...]
    edges: tuple[PropertyGraphEdge, ...]


def build_property_graph() -> PropertyGraph:
    """RFC-MSR01 depends on MeaningMeasurement and defines
    StabilizedTrajectory; RFC-CLE001 refines StabilizedTrajectory;
    MeaningMeasurement is understood in the context of RFC-MM001 (its
    defining specification). Every edge points from a dependent object
    toward the premise it needs — one consistent direction, so the graph
    is a DAG: no node's transitive premises loop back to itself. (An
    earlier version of this fixture also added the reverse edge, RFC-MM001
    "defines" MeaningMeasurement, and produced a 2-cycle
    `MeaningMeasurement <-> RFC-MM001` — the same fact stated from both
    ends at once. `_semantic_closure`'s pullback/pushout root detection
    assumes no node is its own transitive premise, so only one direction
    is kept.)
    """
    nodes = (
        PropertyGraphNode(id="RFC-MM001", category="SpecificationDocument"),
        PropertyGraphNode(id="MeaningMeasurement", category="MeasurementObject"),
        PropertyGraphNode(id="RFC-MSR01", category="SpecificationDocument"),
        PropertyGraphNode(id="StabilizedTrajectory", category="PhaseSpaceTrajectory"),
        PropertyGraphNode(id="RFC-CLE001", category="SpecificationDocument"),
    )
    edges = (
        PropertyGraphEdge(
            id="RFC-MSR01_dependency_MeaningMeasurement",
            source="RFC-MSR01",
            target="MeaningMeasurement",
            kind="dependency",
        ),
        PropertyGraphEdge(
            id="RFC-MSR01_definition_StabilizedTrajectory",
            source="RFC-MSR01",
            target="StabilizedTrajectory",
            kind="definition",
        ),
        PropertyGraphEdge(
            id="RFC-CLE001_refinement_StabilizedTrajectory",
            source="RFC-CLE001",
            target="StabilizedTrajectory",
            kind="refinement",
        ),
        PropertyGraphEdge(
            id="MeaningMeasurement_context_RFC-MM001",
            source="MeaningMeasurement",
            target="RFC-MM001",
            kind="context",
        ),
    )
    return PropertyGraph(nodes=nodes, edges=edges)


__all__ = ["PropertyGraph", "PropertyGraphEdge", "PropertyGraphNode", "build_property_graph"]
