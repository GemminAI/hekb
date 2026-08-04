"""EXP-HEKB001 Stage 5's cross-reference fixture: RFC-MM001 / RFC-MSR01.

Not a Graphify stand-in. Graphify's job is Markdown -> property graph; this
module starts *after* that boundary, constructing `hekb.models.Concept`/
`KnowledgeRelation` values directly — exactly what a real Graphify producer
would eventually hand to HEKB, and squarely inside HEKB's own domain (its
`Protocol`-conformance and category-axiom checks are real, not faked). No
`ProducerLike`/parsing interface is defined here or anywhere in this
experiment; see `docs/RFC_ALIGNMENT.md` for why that's Graphify's own
interface to define, not HEKB's or this harness's.

The `defines`/`consumes` example is the one the EXP-HEKB001 specification
itself names (RFC-MM001 defines `MeaningMeasurement`; RFC-MSR01 consumes
it). Each `(document, relation-kind)` pair gets its own small Concept
(e.g. ``RFC-MM001.defines``) rather than one Concept per document, because
`KnowledgeRelation.mapping` must be *total* over its source's elements —
modeling "this document's full vocabulary" as one object would force a
single morphism to cover every identifier a document touches, collapsing
the very distinction (defines vs. consumes) Stage 5 asks to validate.
"""

from __future__ import annotations

from hekb.models import Concept, KnowledgeRelation


def build_lineage_fixture() -> tuple[tuple[Concept, ...], tuple[KnowledgeRelation, ...]]:
    """RFC-MM001 defines MeaningMeasurement; RFC-MSR01 consumes it and
    defines StabilizedTrajectory. A `MeaningMeasurement_traces_to_RFC-MM001`
    provenance edge lets `hekb.category.KnowledgeCategory.compose` chain
    "what RFC-MSR01 consumes" directly to "what RFC-MM001 defines" as one
    real, checked morphism — genuine lineage traversal, not a fixture that
    only *looks* like one.
    """
    concepts = (
        Concept(id="RFC-MM001.defines", elements=frozenset({"MeaningMeasurement"})),
        Concept(id="RFC-MSR01.consumes", elements=frozenset({"MeaningMeasurement"})),
        Concept(id="RFC-MSR01.defines", elements=frozenset({"StabilizedTrajectory"})),
        Concept(id="MeaningMeasurement", elements=frozenset({"MeaningMeasurement"})),
        Concept(id="StabilizedTrajectory", elements=frozenset({"StabilizedTrajectory"})),
    )
    relations = (
        KnowledgeRelation(
            id="RFC-MM001_defines_MeaningMeasurement",
            source="RFC-MM001.defines",
            target="MeaningMeasurement",
            mapping={"MeaningMeasurement": "MeaningMeasurement"},
            invariants={"relation_kind": 1.0},  # 1.0 == "defines", by this fixture's convention
        ),
        KnowledgeRelation(
            id="RFC-MSR01_consumes_MeaningMeasurement",
            source="RFC-MSR01.consumes",
            target="MeaningMeasurement",
            mapping={"MeaningMeasurement": "MeaningMeasurement"},
            invariants={"relation_kind": 2.0},  # 2.0 == "consumes"
        ),
        KnowledgeRelation(
            id="RFC-MSR01_defines_StabilizedTrajectory",
            source="RFC-MSR01.defines",
            target="StabilizedTrajectory",
            mapping={"StabilizedTrajectory": "StabilizedTrajectory"},
            invariants={"relation_kind": 1.0},
        ),
        KnowledgeRelation(
            id="MeaningMeasurement_traces_to_RFC-MM001",
            source="MeaningMeasurement",
            target="RFC-MM001.defines",
            mapping={"MeaningMeasurement": "MeaningMeasurement"},
            invariants={"relation_kind": 3.0},  # 3.0 == "provenance"
        ),
    )
    return concepts, relations


__all__ = ["build_lineage_fixture"]
