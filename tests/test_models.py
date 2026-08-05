import pytest

from hekb.models import Concept, EpistemicGraphSnapshot, KnowledgeRelation, StorageProfile


def test_concept_holds_element_set() -> None:
    concept = Concept(id="A", elements=frozenset({"a1", "a2"}))
    assert concept.elements == frozenset({"a1", "a2"})
    assert concept.centroid is None


def test_knowledge_relation_holds_mapping() -> None:
    relation = KnowledgeRelation(id="f", source="A", target="B", mapping={"a1": "b1"})
    assert relation.mapping == {"a1": "b1"}


def test_knowledge_relation_defaults_to_uniform_cost() -> None:
    relation = KnowledgeRelation(id="f", source="A", target="B", mapping={})
    assert relation.cost == 1.0


def test_knowledge_relation_rejects_a_negative_cost() -> None:
    with pytest.raises(ValueError, match="non-negative"):
        KnowledgeRelation(id="f", source="A", target="B", mapping={}, cost=-1.0)


def test_storage_profile_matches_declarative_shape() -> None:
    profile = StorageProfile(
        storage_class="relational",
        capabilities={"transactions": True},
        payload_snapshot={"morphism_id": "m1"},
    )
    assert profile.storage_class == "relational"
    assert profile.capabilities == {"transactions": True}


def test_epistemic_graph_snapshot_is_a_plain_value() -> None:
    concept = Concept(id="A", elements=frozenset({"a1"}))
    relation = KnowledgeRelation(id="id_A", source="A", target="A", mapping={"a1": "a1"})
    snapshot = EpistemicGraphSnapshot(vertices=(concept,), edges=(relation,))
    assert snapshot.vertices == (concept,)
    assert snapshot.edges == (relation,)
