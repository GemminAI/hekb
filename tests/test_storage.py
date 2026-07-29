from hekb.models import KnowledgeRelation
from hekb.storage import InMemoryProjectionBackend, to_storage_profile


def test_to_storage_profile_produces_relational_profile() -> None:
    relation = KnowledgeRelation(
        id="m_u_v_stability",
        source="object_A",
        target="object_B",
        mapping={},
        invariants={"kappa_max": 0.045, "potential_drop": 12.45},
    )

    profile = to_storage_profile(relation)

    assert profile.storage_class == "relational"
    assert profile.capabilities == {
        "transactions": True,
        "referential_integrity": True,
        "random_update": True,
    }
    assert profile.payload_snapshot == {
        "morphism_id": "m_u_v_stability",
        "domain": "object_A",
        "codomain": "object_B",
        "invariants": {"kappa_max": 0.045, "potential_drop": 12.45},
    }


def test_in_memory_backend_records_profiles() -> None:
    backend = InMemoryProjectionBackend()
    relation = KnowledgeRelation(id="f", source="A", target="B", mapping={})

    backend.write(to_storage_profile(relation))

    assert len(backend.profiles) == 1
    assert backend.profiles[0].payload_snapshot["morphism_id"] == "f"
