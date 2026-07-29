"""The HEKB algebraic core: category axioms, pushouts, pullbacks, adjunction.

K is modeled as the category of finite sets and functions (Set), which is
both complete and cocomplete with well-known constructive limits/colimits
— that is what makes "universal problems solved deterministically, not via
ad-hoc joins" an actually implementable, testable claim here, rather than
a metaphor.

Continuous-manifold concerns (attractor centroids as real vectors,
Hessians, and any other geometric structure) are treated as opaque
metadata attached to a ``Concept`` (see :mod:`hekb.models`) and are never
computed or interpreted by this module — this module only ever reasons
about the finite Set structure. Dynamic/geometric computation is
deliberately out of scope here; this module only touches the algebraic
skeleton.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from itertools import product
from types import MappingProxyType

from hekb.models import Concept, KnowledgeRelation

_PAIR_SEP = "\x1f"  # ASCII Unit Separator — encodes a tensor pair (a, b)
_FUNC_SEP = "\x1e"  # ASCII Record Separator — encodes a function graph


class CategoryAxiomViolation(ValueError):
    """Raised when an operation would violate a category axiom of K."""


class HomotopyViolation(ValueError):
    """Raised when a proposed update fails the Homotopic Update Law.

    I.e. the commutative square sigma_B . f == U(f) . sigma_A does not hold,
    so the update would rupture K's existing topology if applied.
    """

    def __init__(self, mismatches: dict[str, tuple[str, str]]) -> None:
        self.mismatches = mismatches
        super().__init__(
            f"naturality square does not commute for {len(mismatches)} element(s): {mismatches}"
        )


class KnowledgeCategory:
    """A mutable registry of Concepts and KnowledgeRelations forming K.

    Adding an object or morphism validates the relevant category axioms —
    no incoherent state reaches persistence, enforced here at the
    algebraic layer, before any storage boundary is ever touched.
    """

    def __init__(self) -> None:
        self._objects: dict[str, Concept] = {}
        self._morphisms: dict[str, KnowledgeRelation] = {}

    def add_object(self, concept: Concept) -> None:
        if concept.id in self._objects:
            raise CategoryAxiomViolation(f"object {concept.id!r} already exists")
        self._objects[concept.id] = concept

    def object(self, concept_id: str) -> Concept:
        return self._objects[concept_id]

    @property
    def objects(self) -> Mapping[str, Concept]:
        return MappingProxyType(self._objects)

    @property
    def morphisms(self) -> Mapping[str, KnowledgeRelation]:
        return MappingProxyType(self._morphisms)

    def add_morphism(self, relation: KnowledgeRelation) -> None:
        if relation.id in self._morphisms:
            raise CategoryAxiomViolation(f"morphism {relation.id!r} already exists")
        source = self._objects.get(relation.source)
        target = self._objects.get(relation.target)
        if source is None or target is None:
            raise CategoryAxiomViolation(
                f"morphism {relation.id!r} references an unknown object "
                f"(source={relation.source!r}, target={relation.target!r})"
            )
        if relation.mapping.keys() != source.elements:
            raise CategoryAxiomViolation(
                f"morphism {relation.id!r} is not total over its source's elements: "
                f"domain gap = {source.elements - relation.mapping.keys()}, "
                f"extra keys = {relation.mapping.keys() - source.elements}"
            )
        if not set(relation.mapping.values()) <= target.elements:
            raise CategoryAxiomViolation(
                f"morphism {relation.id!r} maps outside its target's elements: "
                f"{set(relation.mapping.values()) - target.elements}"
            )
        self._morphisms[relation.id] = relation

    def morphism(self, relation_id: str) -> KnowledgeRelation:
        return self._morphisms[relation_id]

    def identity(self, concept_id: str) -> KnowledgeRelation:
        """The identity morphism id_X for object X — MUST exist for every object."""
        concept = self._objects[concept_id]
        return KnowledgeRelation(
            id=f"id_{concept_id}",
            source=concept_id,
            target=concept_id,
            mapping={e: e for e in concept.elements},
        )

    def compose(self, f: KnowledgeRelation, g: KnowledgeRelation) -> KnowledgeRelation:
        """g . f : f.source -> g.target, i.e. apply f then g."""
        if f.target != g.source:
            raise CategoryAxiomViolation(
                f"cannot compose: {f.id!r} targets {f.target!r} but {g.id!r} sources {g.source!r}"
            )
        return KnowledgeRelation(
            id=f"{g.id}_after_{f.id}",
            source=f.source,
            target=g.target,
            mapping={a: g.mapping[b] for a, b in f.mapping.items()},
        )

    # -- Commutativity over mutation --------------------------------------

    def verify_naturality(
        self,
        sigma_a: KnowledgeRelation,
        f: KnowledgeRelation,
        sigma_b: KnowledgeRelation,
        u_f: KnowledgeRelation,
    ) -> None:
        """Assert the naturality square commutes: sigma_B . f == U(f) . sigma_A.

                A --  f  --> B
                |            |
          sigma_a          sigma_b
                |            |
                v            v
               U(A) -- u_f --> U(B)

        Raises :class:`HomotopyViolation` (not a bool) so a caller cannot
        accidentally ignore a broken update — the caller MUST catch this
        and roll back, never persist past it.
        """
        left = self.compose(f, sigma_b)  # sigma_b . f : A -> U(B)
        right = self.compose(sigma_a, u_f)  # u_f . sigma_a : A -> U(B)

        mismatches = {
            a: (left.mapping[a], right.mapping[a])
            for a in left.mapping
            if left.mapping[a] != right.mapping[a]
        }
        if mismatches:
            raise HomotopyViolation(mismatches)

    # -- On-demand universal-property execution ---------------------------

    def pushout(
        self, f: KnowledgeRelation, g: KnowledgeRelation
    ) -> tuple[Concept, KnowledgeRelation, KnowledgeRelation]:
        """Pushout of the span A <--f-- C --g--> B: A |>_C B.

        Returns ``(pushout_object, injection_from_A, injection_from_B)``.
        Constructed as the coequalizer of the disjoint union A + B under
        the relation f(c) ~ g(c) for every c in C — the standard
        construction of pushouts in Set.
        """
        if f.source != g.source:
            raise CategoryAxiomViolation(
                f"pushout requires a common source (span apex): "
                f"{f.id!r} sources {f.source!r}, {g.id!r} sources {g.source!r}"
            )
        object_a = self._objects[f.target]
        object_b = self._objects[g.target]
        common = self._objects[f.source]

        parent: dict[tuple[str, str], tuple[str, str]] = {}

        def find(node: tuple[str, str]) -> tuple[str, str]:
            root = node
            while parent[root] != root:
                root = parent[root]
            while parent[node] != root:
                parent[node], node = root, parent[node]
            return root

        def union(x: tuple[str, str], y: tuple[str, str]) -> None:
            rx, ry = find(x), find(y)
            if rx != ry:
                parent[ry] = rx

        for a in object_a.elements:
            parent[("A", a)] = ("A", a)
        for b in object_b.elements:
            parent[("B", b)] = ("B", b)
        for c in common.elements:
            union(("A", f.mapping[c]), ("B", g.mapping[c]))

        label_of: dict[tuple[str, str], str] = {}

        def label(node: tuple[str, str]) -> str:
            root = find(node)
            if root not in label_of:
                label_of[root] = f"po_{len(label_of)}"
            return label_of[root]

        i_a = {a: label(("A", a)) for a in object_a.elements}
        i_b = {b: label(("B", b)) for b in object_b.elements}
        pushout_elements = frozenset(i_a.values()) | frozenset(i_b.values())

        pushout_object = Concept(
            id=f"{object_a.id}_pushout_{object_b.id}", elements=pushout_elements
        )
        injection_a = KnowledgeRelation(
            id=f"iota_{object_a.id}", source=object_a.id, target=pushout_object.id, mapping=i_a
        )
        injection_b = KnowledgeRelation(
            id=f"iota_{object_b.id}", source=object_b.id, target=pushout_object.id, mapping=i_b
        )
        return pushout_object, injection_a, injection_b

    def pullback(
        self, f: KnowledgeRelation, g: KnowledgeRelation
    ) -> tuple[Concept, KnowledgeRelation, KnowledgeRelation]:
        """Pullback of the cospan A --f--> C <--g-- B: A x_C B.

        Returns ``(pullback_object, projection_to_A, projection_to_B)``.
        Constructed directly as ``{(a, b) : f(a) == g(b)}``, the standard
        construction of pullbacks in Set.
        """
        if f.target != g.target:
            raise CategoryAxiomViolation(
                f"pullback requires a common target (cospan apex): "
                f"{f.id!r} targets {f.target!r}, {g.id!r} targets {g.target!r}"
            )
        object_a = self._objects[f.source]
        object_b = self._objects[g.source]

        matches = [
            (a, b)
            for a, b in product(sorted(object_a.elements), sorted(object_b.elements))
            if f.mapping[a] == g.mapping[b]
        ]
        labels = {pair: f"pb_{i}" for i, pair in enumerate(matches)}

        pullback_elements = frozenset(labels.values())
        proj_a = {labels[(a, b)]: a for (a, b) in matches}
        proj_b = {labels[(a, b)]: b for (a, b) in matches}

        pullback_object = Concept(
            id=f"{object_a.id}_pullback_{object_b.id}", elements=pullback_elements
        )
        projection_a = KnowledgeRelation(
            id=f"pi_{object_a.id}", source=pullback_object.id, target=object_a.id, mapping=proj_a
        )
        projection_b = KnowledgeRelation(
            id=f"pi_{object_b.id}", source=pullback_object.id, target=object_b.id, mapping=proj_b
        )
        return pullback_object, projection_a, projection_b

    def mediating_pushout_morphism(
        self,
        pushout_object: Concept,
        injection_a: KnowledgeRelation,
        injection_b: KnowledgeRelation,
        h_a: KnowledgeRelation,
        h_b: KnowledgeRelation,
    ) -> KnowledgeRelation:
        """The unique u : pushout -> X with u . iota_A == h_A and u . iota_B == h_B.

        Existence requires h_A and h_B to already agree on the identified
        elements (the universal property's precondition); this method
        both verifies that precondition and constructs u, so a caller gets
        "the mediating morphism exists and is unique" as one checked call.
        """
        mapping: dict[str, str] = {}
        for a, po_elem in injection_a.mapping.items():
            image = h_a.mapping[a]
            if po_elem in mapping and mapping[po_elem] != image:
                raise CategoryAxiomViolation(
                    f"no mediating morphism exists: pushout element {po_elem!r} "
                    f"would need to map to both {mapping[po_elem]!r} and {image!r}"
                )
            mapping[po_elem] = image
        for b, po_elem in injection_b.mapping.items():
            image = h_b.mapping[b]
            if po_elem in mapping and mapping[po_elem] != image:
                raise CategoryAxiomViolation(
                    f"no mediating morphism exists: pushout element {po_elem!r} "
                    f"would need to map to both {mapping[po_elem]!r} and {image!r}"
                )
            mapping[po_elem] = image

        return KnowledgeRelation(
            id=f"mediate_{pushout_object.id}",
            source=pushout_object.id,
            target=h_a.target,
            mapping=mapping,
        )

    # -- Algebraic implication and adjunction of inference -----------------

    def tensor(self, a: Concept, b: Concept) -> Concept:
        """The monoidal product A (x) B, modeled as the Cartesian product of Sets."""
        elements = frozenset(encode_pair(x, y) for x in a.elements for y in b.elements)
        return Concept(id=f"{a.id}(x){b.id}", elements=elements)

    def internal_hom(self, b: Concept, c: Concept) -> Concept:
        """The internal hom [B, C], modeled as the set of all total functions B -> C.

        Each element of the returned Concept is a canonical string encoding
        of one such function's graph, produced by :func:`encode_function`.
        """
        elements = frozenset(
            encode_function(dict(zip(sorted(b.elements), combo, strict=True)))
            for combo in product(sorted(c.elements), repeat=len(b.elements))
        )
        return Concept(id=f"[{b.id},{c.id}]", elements=elements)

    def curry(self, f: KnowledgeRelation, a: Concept, b: Concept, c: Concept) -> KnowledgeRelation:
        """Hom(A (x) B, C) -> Hom(A, [B, C]): curry f : A(x)B -> C into A -> [B,C]."""
        mapping = {}
        for a_elem in a.elements:
            partial = {b_elem: f.mapping[encode_pair(a_elem, b_elem)] for b_elem in b.elements}
            mapping[a_elem] = encode_function(partial)
        return KnowledgeRelation(
            id=f"curry_{f.id}", source=a.id, target=f"[{b.id},{c.id}]", mapping=mapping
        )

    def uncurry(
        self, g: KnowledgeRelation, a: Concept, b: Concept, c: Concept
    ) -> KnowledgeRelation:
        """Hom(A, [B, C]) -> Hom(A (x) B, C): the inverse of :meth:`curry`.

        Composed with :meth:`curry`, this witnesses the adjunction
        isomorphism Hom(A(x)B, C) ~= Hom(A, [B,C]) as an executable
        round-trip, not just an asserted equation.
        """
        mapping = {}
        for a_elem in a.elements:
            function = decode_function(g.mapping[a_elem])
            for b_elem in b.elements:
                mapping[encode_pair(a_elem, b_elem)] = function[b_elem]
        return KnowledgeRelation(
            id=f"uncurry_{g.id}", source=f"{a.id}(x){b.id}", target=c.id, mapping=mapping
        )


def encode_pair(a: str, b: str) -> str:
    return f"{a}{_PAIR_SEP}{b}"


def decode_pair(encoded: str) -> tuple[str, str]:
    a, b = encoded.split(_PAIR_SEP)
    return a, b


def encode_function(mapping: dict[str, str]) -> str:
    return _FUNC_SEP.join(encode_pair(x, fx) for x, fx in sorted(mapping.items()))


def decode_function(encoded: str) -> dict[str, str]:
    if not encoded:
        return {}
    return dict(decode_pair(term) for term in encoded.split(_FUNC_SEP))


def compose_all(
    category: KnowledgeCategory, relations: Iterable[KnowledgeRelation]
) -> KnowledgeRelation:
    """Fold :meth:`KnowledgeCategory.compose` over a chain f_1, f_2, ..., f_n."""
    it = iter(relations)
    acc = next(it)
    for relation in it:
        acc = category.compose(acc, relation)
    return acc
