import pytest

from hekb.category import KnowledgeCategory
from hekb.models import Concept, KnowledgeRelation
from hekb.query import geodesic, nearest, neighbours


@pytest.fixture
def positioned_category() -> KnowledgeCategory:
    cat = KnowledgeCategory()
    cat.add_object(Concept(id="A", elements=frozenset({"a1"}), centroid=(0.0, 0.0)))
    cat.add_object(Concept(id="B", elements=frozenset({"b1"}), centroid=(1.0, 0.0)))
    cat.add_object(Concept(id="C", elements=frozenset({"c1"}), centroid=(5.0, 0.0)))
    cat.add_object(Concept(id="D", elements=frozenset({"d1"})))  # no centroid
    return cat


# --- nearest --------------------------------------------------------------


def test_nearest_returns_closest_concepts_sorted_by_distance(
    positioned_category: KnowledgeCategory,
) -> None:
    hits = nearest(positioned_category, (0.0, 0.0), 2)
    assert [hit.concept.id for hit in hits] == ["A", "B"]
    assert hits[0].distance == pytest.approx(0.0)
    assert hits[1].distance == pytest.approx(1.0)


def test_nearest_excludes_concepts_without_a_centroid(
    positioned_category: KnowledgeCategory,
) -> None:
    hits = nearest(positioned_category, (0.0, 0.0), 10)
    assert "D" not in {hit.concept.id for hit in hits}
    assert len(hits) == 3


def test_nearest_ties_break_on_concept_id() -> None:
    cat = KnowledgeCategory()
    cat.add_object(Concept(id="B", elements=frozenset(), centroid=(1.0, 0.0)))
    cat.add_object(Concept(id="A", elements=frozenset(), centroid=(1.0, 0.0)))
    hits = nearest(cat, (0.0, 0.0), 2)
    assert [hit.concept.id for hit in hits] == ["A", "B"]


def test_nearest_rejects_a_non_positive_count(positioned_category: KnowledgeCategory) -> None:
    with pytest.raises(ValueError, match="count must be positive"):
        nearest(positioned_category, (0.0, 0.0), 0)


def test_nearest_rejects_a_dimension_mismatch(positioned_category: KnowledgeCategory) -> None:
    with pytest.raises(ValueError, match="dimension mismatch"):
        nearest(positioned_category, (0.0, 0.0, 0.0), 1)


def test_nearest_over_an_empty_category_is_empty() -> None:
    assert nearest(KnowledgeCategory(), (0.0, 0.0), 1) == ()


# --- neighbours -------------------------------------------------------------


def test_neighbours_returns_outgoing_morphisms_cheapest_first() -> None:
    cat = KnowledgeCategory()
    for concept_id in ("A", "B", "C"):
        cat.add_object(Concept(id=concept_id, elements=frozenset()))
    expensive = KnowledgeRelation(id="f", source="A", target="C", mapping={}, cost=5.0)
    cheap = KnowledgeRelation(id="g", source="A", target="B", mapping={}, cost=1.0)
    cat.add_morphism(expensive)
    cat.add_morphism(cheap)

    result = neighbours(cat, "A")
    assert [edge.id for edge in result] == ["g", "f"]


def test_neighbours_of_an_unknown_concept_raises_key_error(
    positioned_category: KnowledgeCategory,
) -> None:
    with pytest.raises(KeyError):
        neighbours(positioned_category, "nonexistent")


def test_neighbours_with_no_outgoing_edges_is_empty(
    positioned_category: KnowledgeCategory,
) -> None:
    assert neighbours(positioned_category, "C") == ()


# --- geodesic -----------------------------------------------------------------


def test_geodesic_from_a_node_to_itself_is_trivial(
    positioned_category: KnowledgeCategory,
) -> None:
    path = geodesic(positioned_category, "A", "A")
    assert path.concept_ids == ("A",)
    assert path.total_cost == 0.0
    assert path.reachable is True


def test_geodesic_finds_the_minimum_cost_path() -> None:
    cat = KnowledgeCategory()
    for concept_id in ("A", "B", "C"):
        cat.add_object(Concept(id=concept_id, elements=frozenset()))
    cat.add_morphism(KnowledgeRelation(id="direct", source="A", target="C", mapping={}, cost=10.0))
    cat.add_morphism(KnowledgeRelation(id="a_b", source="A", target="B", mapping={}, cost=1.0))
    cat.add_morphism(KnowledgeRelation(id="b_c", source="B", target="C", mapping={}, cost=1.0))

    path = geodesic(cat, "A", "C")
    assert path.concept_ids == ("A", "B", "C")
    assert path.total_cost == pytest.approx(2.0)
    assert path.reachable is True


def test_geodesic_reports_an_unreachable_pair() -> None:
    cat = KnowledgeCategory()
    cat.add_object(Concept(id="A", elements=frozenset()))
    cat.add_object(Concept(id="B", elements=frozenset()))
    path = geodesic(cat, "A", "B")
    assert path.concept_ids == ()
    assert path.total_cost == float("inf")
    assert path.reachable is False


def test_geodesic_with_an_unknown_source_or_target_raises_key_error(
    positioned_category: KnowledgeCategory,
) -> None:
    with pytest.raises(KeyError):
        geodesic(positioned_category, "nonexistent", "A")
    with pytest.raises(KeyError):
        geodesic(positioned_category, "A", "nonexistent")


def test_geodesic_skips_a_stale_queue_entry_and_a_worse_relaxation() -> None:
    """A -> C direct (cost 4) is queued before B -> C (cost 2) improves it, and
    C -> D (cost 100) never beats the B -> D (cost 1) route already found —
    exercising both the stale-entry skip and the failed-relaxation branch."""
    cat = KnowledgeCategory()
    for concept_id in ("A", "B", "C", "D", "F"):
        cat.add_object(Concept(id=concept_id, elements=frozenset()))
    cat.add_morphism(KnowledgeRelation(id="ab", source="A", target="B", mapping={}, cost=1.0))
    cat.add_morphism(KnowledgeRelation(id="ac", source="A", target="C", mapping={}, cost=4.0))
    cat.add_morphism(KnowledgeRelation(id="bc", source="B", target="C", mapping={}, cost=1.0))
    cat.add_morphism(KnowledgeRelation(id="bd", source="B", target="D", mapping={}, cost=1.0))
    cat.add_morphism(KnowledgeRelation(id="cd", source="C", target="D", mapping={}, cost=100.0))
    cat.add_morphism(KnowledgeRelation(id="cf", source="C", target="F", mapping={}, cost=10.0))

    path = geodesic(cat, "A", "F")
    assert path.concept_ids == ("A", "B", "C", "F")
    assert path.total_cost == pytest.approx(12.0)
    assert path.reachable is True
