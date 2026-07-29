import pytest

from hekb.category import (
    CategoryAxiomViolation,
    HomotopyViolation,
    KnowledgeCategory,
    compose_all,
    decode_function,
    encode_pair,
)
from hekb.models import Concept, KnowledgeRelation


def test_identity_is_neutral_for_composition(category: KnowledgeCategory) -> None:
    f = KnowledgeRelation(id="f", source="A", target="B", mapping={"a1": "b1", "a2": "b2"})
    category.add_morphism(f)

    id_a = category.identity("A")
    id_b = category.identity("B")

    assert category.compose(id_a, f).mapping == f.mapping
    assert category.compose(f, id_b).mapping == f.mapping


def test_add_morphism_rejects_non_total_mapping(category: KnowledgeCategory) -> None:
    partial = KnowledgeRelation(id="bad", source="A", target="B", mapping={"a1": "b1"})

    with pytest.raises(CategoryAxiomViolation, match="not total"):
        category.add_morphism(partial)


def test_add_morphism_rejects_mapping_outside_target(category: KnowledgeCategory) -> None:
    bad = KnowledgeRelation(id="bad", source="A", target="B", mapping={"a1": "nope", "a2": "b2"})

    with pytest.raises(CategoryAxiomViolation, match="maps outside"):
        category.add_morphism(bad)


def test_compose_rejects_mismatched_boundary(category: KnowledgeCategory) -> None:
    f = KnowledgeRelation(id="f", source="A", target="B", mapping={"a1": "b1", "a2": "b2"})
    h = KnowledgeRelation(id="h", source="A", target="C", mapping={"a1": "c1", "a2": "c1"})
    category.add_morphism(f)
    category.add_morphism(h)

    with pytest.raises(CategoryAxiomViolation, match="cannot compose"):
        category.compose(f, h)  # f targets B, h sources A -- not composable


def test_verify_naturality_passes_on_commuting_square() -> None:
    cat = KnowledgeCategory()
    cat.add_object(Concept(id="A", elements=frozenset({"a1"})))
    cat.add_object(Concept(id="B", elements=frozenset({"b1"})))
    cat.add_object(Concept(id="UA", elements=frozenset({"ua1"})))
    cat.add_object(Concept(id="UB", elements=frozenset({"ub1"})))

    f = KnowledgeRelation(id="f", source="A", target="B", mapping={"a1": "b1"})
    sigma_a = KnowledgeRelation(id="sigma_a", source="A", target="UA", mapping={"a1": "ua1"})
    sigma_b = KnowledgeRelation(id="sigma_b", source="B", target="UB", mapping={"b1": "ub1"})
    u_f = KnowledgeRelation(id="u_f", source="UA", target="UB", mapping={"ua1": "ub1"})
    for m in (f, sigma_a, sigma_b, u_f):
        cat.add_morphism(m)

    cat.verify_naturality(sigma_a, f, sigma_b, u_f)  # must not raise


def test_verify_naturality_raises_on_broken_square() -> None:
    cat = KnowledgeCategory()
    cat.add_object(Concept(id="A", elements=frozenset({"a1"})))
    cat.add_object(Concept(id="B", elements=frozenset({"b1"})))
    cat.add_object(Concept(id="UA", elements=frozenset({"ua1"})))
    cat.add_object(Concept(id="UB", elements=frozenset({"ub1", "ub2"})))

    f = KnowledgeRelation(id="f", source="A", target="B", mapping={"a1": "b1"})
    sigma_a = KnowledgeRelation(id="sigma_a", source="A", target="UA", mapping={"a1": "ua1"})
    sigma_b = KnowledgeRelation(id="sigma_b", source="B", target="UB", mapping={"b1": "ub1"})
    # u_f deliberately sends ua1 to ub2, disagreeing with sigma_b . f == ub1
    u_f = KnowledgeRelation(id="u_f", source="UA", target="UB", mapping={"ua1": "ub2"})
    for m in (f, sigma_a, sigma_b, u_f):
        cat.add_morphism(m)

    with pytest.raises(HomotopyViolation):
        cat.verify_naturality(sigma_a, f, sigma_b, u_f)


def test_pushout_identifies_shared_image(category: KnowledgeCategory) -> None:
    f = KnowledgeRelation(id="f", source="C", target="A", mapping={"c1": "a1"})
    g = KnowledgeRelation(id="g", source="C", target="B", mapping={"c1": "b1"})
    category.add_morphism(f)
    category.add_morphism(g)

    pushout_object, iota_a, iota_b = category.pushout(f, g)

    assert len(pushout_object.elements) == 3  # {a1~b1}, a2, b2
    assert iota_a.mapping["a1"] == iota_b.mapping["b1"]
    assert iota_a.mapping["a2"] != iota_a.mapping["a1"]
    assert iota_b.mapping["b2"] != iota_a.mapping["a1"]


def test_pushout_mediating_morphism_exists_and_is_unique(category: KnowledgeCategory) -> None:
    f = KnowledgeRelation(id="f", source="C", target="A", mapping={"c1": "a1"})
    g = KnowledgeRelation(id="g", source="C", target="B", mapping={"c1": "b1"})
    category.add_morphism(f)
    category.add_morphism(g)
    pushout_object, iota_a, iota_b = category.pushout(f, g)

    category.add_object(Concept(id="X", elements=frozenset({"x1", "x2", "x3"})))
    h_a = KnowledgeRelation(id="h_a", source="A", target="X", mapping={"a1": "x1", "a2": "x2"})
    # h_b agrees with h_a on the identified element (b1 maps where a1 maps: x1)
    h_b = KnowledgeRelation(id="h_b", source="B", target="X", mapping={"b1": "x1", "b2": "x3"})

    mediator = category.mediating_pushout_morphism(pushout_object, iota_a, iota_b, h_a, h_b)

    # u . iota_A == h_A and u . iota_B == h_B
    assert category.compose(iota_a, mediator).mapping == h_a.mapping
    assert category.compose(iota_b, mediator).mapping == h_b.mapping


def test_pushout_mediating_morphism_rejects_inconsistent_cocone(
    category: KnowledgeCategory,
) -> None:
    f = KnowledgeRelation(id="f", source="C", target="A", mapping={"c1": "a1"})
    g = KnowledgeRelation(id="g", source="C", target="B", mapping={"c1": "b1"})
    category.add_morphism(f)
    category.add_morphism(g)
    pushout_object, iota_a, iota_b = category.pushout(f, g)

    category.add_object(Concept(id="X", elements=frozenset({"x1", "x2"})))
    h_a = KnowledgeRelation(id="h_a", source="A", target="X", mapping={"a1": "x1", "a2": "x2"})
    # h_b disagrees with h_a on the identified element (b1 -> x2, but a1 -> x1)
    h_b = KnowledgeRelation(id="h_b", source="B", target="X", mapping={"b1": "x2", "b2": "x1"})

    with pytest.raises(CategoryAxiomViolation, match="no mediating morphism exists"):
        category.mediating_pushout_morphism(pushout_object, iota_a, iota_b, h_a, h_b)


def test_pullback_filters_to_matching_preimages() -> None:
    cat = KnowledgeCategory()
    cat.add_object(Concept(id="A", elements=frozenset({"a1", "a2"})))
    cat.add_object(Concept(id="B", elements=frozenset({"b1", "b2"})))
    cat.add_object(Concept(id="C", elements=frozenset({"c1", "c2"})))
    f = KnowledgeRelation(id="f", source="A", target="C", mapping={"a1": "c1", "a2": "c2"})
    g = KnowledgeRelation(id="g", source="B", target="C", mapping={"b1": "c1", "b2": "c2"})
    cat.add_morphism(f)
    cat.add_morphism(g)

    pullback_object, pi_a, pi_b = cat.pullback(f, g)

    # only (a1,b1) and (a2,b2) agree; (a1,b2) and (a2,b1) do not
    assert len(pullback_object.elements) == 2
    pairs = {(pi_a.mapping[e], pi_b.mapping[e]) for e in pullback_object.elements}
    assert pairs == {("a1", "b1"), ("a2", "b2")}


def test_tensor_and_curry_uncurry_round_trip() -> None:
    cat = KnowledgeCategory()
    a = Concept(id="A", elements=frozenset({"a1", "a2"}))
    b = Concept(id="B", elements=frozenset({"b1", "b2"}))
    c = Concept(id="C", elements=frozenset({"c1", "c2"}))
    for concept in (a, b, c):
        cat.add_object(concept)

    tensor_ab = cat.tensor(a, b)
    cat.add_object(tensor_ab)

    # an arbitrary total function A(x)B -> C
    f = KnowledgeRelation(
        id="f",
        source=tensor_ab.id,
        target="C",
        mapping={
            encode_pair("a1", "b1"): "c1",
            encode_pair("a1", "b2"): "c2",
            encode_pair("a2", "b1"): "c2",
            encode_pair("a2", "b2"): "c1",
        },
    )
    cat.add_morphism(f)

    curried = cat.curry(f, a, b, c)
    uncurried = cat.uncurry(curried, a, b, c)

    assert uncurried.mapping == f.mapping  # round trip: Hom(A(x)B,C) ~= Hom(A,[B,C])

    # spot-check curry itself: curried(a1) is a function B->C sending b1->c1, b2->c2
    decoded = decode_function(curried.mapping["a1"])
    assert decoded == {"b1": "c1", "b2": "c2"}


def test_internal_hom_enumerates_all_functions() -> None:
    cat = KnowledgeCategory()
    b = Concept(id="B", elements=frozenset({"b1", "b2"}))
    c = Concept(id="C", elements=frozenset({"c1", "c2"}))

    hom_bc = cat.internal_hom(b, c)

    assert len(hom_bc.elements) == 4  # 2^2 total functions B -> C


def test_compose_all_folds_a_chain_of_morphisms(category: KnowledgeCategory) -> None:
    f = KnowledgeRelation(id="f", source="A", target="B", mapping={"a1": "b1", "a2": "b2"})
    g = KnowledgeRelation(id="g", source="B", target="C", mapping={"b1": "c1", "b2": "c1"})
    category.add_morphism(f)
    category.add_morphism(g)

    folded = compose_all(category, [f, g])

    assert folded.source == "A"
    assert folded.target == "C"
    assert folded.mapping == category.compose(f, g).mapping


def test_compose_all_single_relation_is_a_no_op_fold(category: KnowledgeCategory) -> None:
    f = KnowledgeRelation(id="f", source="A", target="B", mapping={"a1": "b1", "a2": "b2"})
    category.add_morphism(f)

    assert compose_all(category, [f]).mapping == f.mapping
