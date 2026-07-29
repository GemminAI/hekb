import pytest

from hekb.category import CategoryAxiomViolation, HomotopyViolation
from hekb.models import Concept, KnowledgeRelation
from hekb.runtime import HEKBCoreRuntime
from hekb.storage import InMemoryProjectionBackend


def test_ingest_morphism_persists_a_storage_profile() -> None:
    backend = InMemoryProjectionBackend()
    runtime = HEKBCoreRuntime(backend)
    runtime.ingest_object(Concept(id="A", elements=frozenset({"a1"})))
    runtime.ingest_object(Concept(id="B", elements=frozenset({"b1"})))

    runtime.ingest_morphism(KnowledgeRelation(id="f", source="A", target="B", mapping={"a1": "b1"}))

    assert len(backend.profiles) == 1
    assert backend.profiles[0].payload_snapshot["morphism_id"] == "f"


def test_ingest_morphism_axiom_violation_persists_nothing() -> None:
    backend = InMemoryProjectionBackend()
    runtime = HEKBCoreRuntime(backend)
    runtime.ingest_object(Concept(id="A", elements=frozenset({"a1", "a2"})))
    runtime.ingest_object(Concept(id="B", elements=frozenset({"b1"})))

    with pytest.raises(CategoryAxiomViolation, match="not total"):
        runtime.ingest_morphism(
            KnowledgeRelation(id="bad", source="A", target="B", mapping={"a1": "b1"})
        )

    assert backend.profiles == ()


def test_ingest_update_rejects_broken_naturality_and_persists_nothing() -> None:
    backend = InMemoryProjectionBackend()
    runtime = HEKBCoreRuntime(backend)
    for concept in (
        Concept(id="A", elements=frozenset({"a1"})),
        Concept(id="B", elements=frozenset({"b1"})),
        Concept(id="UA", elements=frozenset({"ua1"})),
        Concept(id="UB", elements=frozenset({"ub1", "ub2"})),
    ):
        runtime.ingest_object(concept)

    f = KnowledgeRelation(id="f", source="A", target="B", mapping={"a1": "b1"})
    sigma_a = KnowledgeRelation(id="sigma_a", source="A", target="UA", mapping={"a1": "ua1"})
    sigma_b = KnowledgeRelation(id="sigma_b", source="B", target="UB", mapping={"b1": "ub1"})
    broken_u_f = KnowledgeRelation(id="u_f", source="UA", target="UB", mapping={"ua1": "ub2"})
    for m in (f, sigma_a, sigma_b):
        runtime.ingest_morphism(m)

    with pytest.raises(HomotopyViolation):
        runtime.ingest_update(sigma_a, f, sigma_b, broken_u_f)

    assert "u_f" not in runtime.category.morphisms
    assert len(backend.profiles) == 3  # only f, sigma_a, sigma_b -- never u_f


def test_export_epistemic_graph_is_a_frozen_snapshot() -> None:
    backend = InMemoryProjectionBackend()
    runtime = HEKBCoreRuntime(backend)
    runtime.ingest_object(Concept(id="A", elements=frozenset({"a1"})))

    snapshot_1 = runtime.export_epistemic_graph()
    runtime.ingest_object(Concept(id="B", elements=frozenset({"b1"})))
    snapshot_2 = runtime.export_epistemic_graph()

    assert len(snapshot_1.vertices) == 1
    assert len(snapshot_2.vertices) == 2  # later mutation doesn't retroactively change snapshot_1
