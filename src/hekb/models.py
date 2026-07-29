"""Domain models for the HEKB algebraic core.

The knowledge category K is modeled concretely as the category of finite
sets and functions (Set): a ``Concept`` is an object of K represented by
its underlying finite element set (plus optional geometric metadata
supplied by a caller), and a ``KnowledgeRelation`` is a morphism of K
represented by a total function between two Concepts' element sets. This
gives every algebraic operation in :mod:`hekb.category` (composition,
pushout, pullback, the tensor/internal-hom adjunction) a constructive,
exactly checkable implementation instead of an abstract one.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True, slots=True)
class Concept:
    """An object of the knowledge category K.

    ``elements`` is the underlying finite set K's Set-model represents
    this object with. ``centroid``/``hessian``/``invariants`` are optional
    geometric metadata slots a caller may populate from whatever upstream
    system tracks that geometry (see
    :meth:`hekb.runtime.HEKBCoreRuntime.export_epistemic_graph`); HEKB's
    algebraic core never computes or interprets them itself — it only
    carries them through as opaque payload.
    """

    id: str
    elements: frozenset[str]
    centroid: tuple[float, ...] | None = None
    hessian: tuple[tuple[float, ...], ...] | None = None
    invariants: dict[str, float] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class KnowledgeRelation:
    """A morphism of K: a total function ``source.elements -> target.elements``.

    ``mapping`` MUST be total over ``source``'s element set (every element
    of the domain Concept has an image) — this is enforced by
    :meth:`hekb.category.KnowledgeCategory.add_morphism`, not by this
    dataclass itself, so a ``KnowledgeRelation`` can be constructed and
    validated against a specific category.
    """

    id: str
    source: str
    target: str
    mapping: dict[str, str]
    invariants: dict[str, float] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class StorageProfile:
    """A sovereign, declarative storage profile emitted by the runtime.

    Absolutely free of any concrete database execution (see
    :mod:`hekb.storage`) — this is a plain, inert data value; nothing in
    this module or :mod:`hekb.category` imports a database driver.
    """

    storage_class: str
    capabilities: dict[str, bool] = field(default_factory=dict)
    payload_snapshot: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class EpistemicGraphSnapshot:
    """A frozen, immutable export of K for downstream consumers.

    ``vertices``/``edges`` are plain tuples of Concept/KnowledgeRelation
    values at export time — a value, not a live view, so any consumer
    always compiles or reads against a stable snapshot.
    """

    vertices: tuple[Concept, ...]
    edges: tuple[KnowledgeRelation, ...]
