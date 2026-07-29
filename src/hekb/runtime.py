"""HEKBCoreRuntime: the facade wiring the algebraic core to a storage boundary.

This is HEKB's runtime surface: it owns a
:class:`~hekb.category.KnowledgeCategory` (the in-memory algebraic state)
and a :class:`~hekb.storage.ProjectionBackend` (the storage-ignorant
persistence boundary), and enforces that nothing reaches the backend
without first passing the relevant category-theoretic check.
"""

from __future__ import annotations

from hekb.category import HomotopyViolation, KnowledgeCategory
from hekb.models import Concept, EpistemicGraphSnapshot, KnowledgeRelation
from hekb.storage import ProjectionBackend, to_storage_profile


class HEKBCoreRuntime:
    def __init__(self, backend: ProjectionBackend) -> None:
        self._category = KnowledgeCategory()
        self._backend = backend

    @property
    def category(self) -> KnowledgeCategory:
        return self._category

    def ingest_object(self, concept: Concept) -> None:
        self._category.add_object(concept)

    def ingest_morphism(self, relation: KnowledgeRelation) -> None:
        """Admit a new morphism and persist it declaratively.

        Validates category axioms (via
        :meth:`KnowledgeCategory.add_morphism`) *before* touching the
        backend — an axiom violation raises and nothing is persisted:
        validating before mutating, rather than mutating then rolling
        back.
        """
        self._category.add_morphism(relation)
        self._backend.write(to_storage_profile(relation))

    def ingest_update(
        self,
        sigma_a: KnowledgeRelation,
        f: KnowledgeRelation,
        sigma_b: KnowledgeRelation,
        u_f: KnowledgeRelation,
    ) -> None:
        """Admit an update U, gated by the Homotopic Update Law.

        Raises :class:`~hekb.category.HomotopyViolation` — and persists
        nothing — if the naturality square does not commute. Only on
        success is ``u_f`` added to K and persisted.
        """
        self._category.verify_naturality(sigma_a, f, sigma_b, u_f)
        self._category.add_morphism(u_f)
        self._backend.write(to_storage_profile(u_f))

    def export_epistemic_graph(self) -> EpistemicGraphSnapshot:
        """Export a frozen, immutable snapshot of K for downstream consumers.

        Every call returns a new, independent snapshot value — mutating
        the runtime afterward never retroactively changes a snapshot
        already handed out.
        """
        return EpistemicGraphSnapshot(
            vertices=tuple(self._category.objects.values()),
            edges=tuple(self._category.morphisms.values()),
        )


__all__ = ["HEKBCoreRuntime", "HomotopyViolation"]
