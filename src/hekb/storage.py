"""Total Storage Ignorance: the persistence boundary HEKB defines but never crosses.

HEKB's algebraic core never imports a database driver, never issues
SQL/CQL, and never performs raw disk I/O. Persistence happens exclusively
by constructing a :class:`~hekb.models.StorageProfile` and handing it to a
``ProjectionBackend`` — a boundary this module defines but never crosses.

``tests/test_storage_ignorance_audit.py`` statically enforces this via an
AST scan of this package.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from hekb.models import KnowledgeRelation, StorageProfile


@runtime_checkable
class ProjectionBackend(Protocol):
    """Anything that can durably record a StorageProfile.

    Concrete backends (PostgreSQL, ScyllaDB, S3, ...) implement this
    protocol in a *separate* package/module that HEKB's own core never
    imports — the dependency points from the backend to this Protocol,
    never the reverse.
    """

    def write(self, profile: StorageProfile) -> None: ...


class InMemoryProjectionBackend:
    """A fake backend for tests and standalone demos — not a real store.

    Deliberately trivial: it exists so :mod:`hekb.runtime` can be
    exercised end-to-end without HEKB ever depending on a real database,
    keeping storage ignorance true by construction rather than by
    discipline alone.
    """

    def __init__(self) -> None:
        self._profiles: list[StorageProfile] = []

    def write(self, profile: StorageProfile) -> None:
        self._profiles.append(profile)

    @property
    def profiles(self) -> tuple[StorageProfile, ...]:
        return tuple(self._profiles)


def to_storage_profile(relation: KnowledgeRelation) -> StorageProfile:
    """Convert a committed KnowledgeRelation into its declarative StorageProfile.

    A relational storage class with transactional/referential-integrity
    capabilities, and a payload snapshot carrying the morphism's identity
    and invariants — never a SQL statement or a driver call.
    """
    return StorageProfile(
        storage_class="relational",
        capabilities={
            "transactions": True,
            "referential_integrity": True,
            "random_update": True,
        },
        payload_snapshot={
            "morphism_id": relation.id,
            "domain": relation.source,
            "codomain": relation.target,
            "invariants": dict(relation.invariants),
        },
    )
