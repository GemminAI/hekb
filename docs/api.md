# HEKB API Reference

All public names below are importable directly from the top-level
`hekb` package (e.g. `from hekb import Concept`), as well as from their
defining submodule.

## `hekb.models`

### `Concept`

```python
@dataclass(frozen=True, slots=True)
class Concept:
    id: str
    elements: frozenset[str]
    centroid: tuple[float, ...] | None = None
    hessian: tuple[tuple[float, ...], ...] | None = None
    invariants: dict[str, float] = field(default_factory=dict)
```

An object of the knowledge category K. `elements` is the finite set K's
Set-model represents this object with. `centroid`/`hessian`/`invariants`
are optional metadata slots HEKB never computes or interprets itself.

### `KnowledgeRelation`

```python
@dataclass(frozen=True, slots=True)
class KnowledgeRelation:
    id: str
    source: str
    target: str
    mapping: dict[str, str]
    invariants: dict[str, float] = field(default_factory=dict)
```

A morphism of K: a (claimed) total function `source.elements ->
target.elements`. Totality and codomain-membership are enforced by
`KnowledgeCategory.add_morphism`, not by this dataclass.

### `StorageProfile`

```python
@dataclass(frozen=True, slots=True)
class StorageProfile:
    storage_class: str
    capabilities: dict[str, bool] = field(default_factory=dict)
    payload_snapshot: dict[str, Any] = field(default_factory=dict)
```

A declarative, inert description of what should be persisted — never a
SQL statement or driver call. Produced by `hekb.storage.to_storage_profile`.

### `EpistemicGraphSnapshot`

```python
@dataclass(frozen=True, slots=True)
class EpistemicGraphSnapshot:
    vertices: tuple[Concept, ...]
    edges: tuple[KnowledgeRelation, ...]
```

A frozen, immutable export of K, returned by
`HEKBCoreRuntime.export_epistemic_graph`.

## `hekb.category`

### `KnowledgeCategory`

A mutable registry of `Concept` objects and `KnowledgeRelation` morphisms
forming K.

| Method | Signature | Behavior |
|---|---|---|
| `add_object` | `(concept: Concept) -> None` | Raises `CategoryAxiomViolation` if `concept.id` already exists. |
| `object` | `(concept_id: str) -> Concept` | Lookup by id. |
| `objects` | property `-> Mapping[str, Concept]` | Read-only view of all objects. |
| `add_morphism` | `(relation: KnowledgeRelation) -> None` | Raises `CategoryAxiomViolation` if the id already exists, source/target are unknown, the mapping is non-total over the source's elements, or maps outside the target's elements. |
| `morphism` | `(relation_id: str) -> KnowledgeRelation` | Lookup by id. |
| `morphisms` | property `-> Mapping[str, KnowledgeRelation]` | Read-only view of all morphisms. |
| `identity` | `(concept_id: str) -> KnowledgeRelation` | The identity morphism `id_X` for object `X`. |
| `compose` | `(f, g) -> KnowledgeRelation` | `g . f`; raises `CategoryAxiomViolation` if `f.target != g.source`. |
| `verify_naturality` | `(sigma_a, f, sigma_b, u_f) -> None` | Raises `HomotopyViolation` if the naturality square doesn't commute. |
| `pushout` | `(f, g) -> tuple[Concept, KnowledgeRelation, KnowledgeRelation]` | Pushout of a common-source span; returns `(pushout_object, injection_a, injection_b)`. |
| `pullback` | `(f, g) -> tuple[Concept, KnowledgeRelation, KnowledgeRelation]` | Pullback of a common-target cospan; returns `(pullback_object, projection_a, projection_b)`. |
| `mediating_pushout_morphism` | `(pushout_object, injection_a, injection_b, h_a, h_b) -> KnowledgeRelation` | The unique morphism out of a pushout satisfying the universal property; raises `CategoryAxiomViolation` if `h_a`/`h_b` disagree on identified elements. |
| `tensor` | `(a: Concept, b: Concept) -> Concept` | The monoidal product `A ⊗ B`. |
| `internal_hom` | `(b: Concept, c: Concept) -> Concept` | `[B, C]`, the set of all total functions `B -> C`. |
| `curry` | `(f, a, b, c) -> KnowledgeRelation` | `Hom(A⊗B, C) -> Hom(A, [B,C])`. |
| `uncurry` | `(g, a, b, c) -> KnowledgeRelation` | Inverse of `curry`. |

### Exceptions

- `CategoryAxiomViolation(ValueError)` — a category axiom was violated.
- `HomotopyViolation(ValueError)` — a proposed update's naturality square
  doesn't commute. Carries `.mismatches: dict[str, tuple[str, str]]`
  (element → `(left_image, right_image)`) describing exactly where.

### Helpers

- `encode_pair(a: str, b: str) -> str` / `decode_pair(encoded: str) -> tuple[str, str]`
- `encode_function(mapping: dict[str, str]) -> str` / `decode_function(encoded: str) -> dict[str, str]`
- `compose_all(category: KnowledgeCategory, relations: Iterable[KnowledgeRelation]) -> KnowledgeRelation` — folds `compose` over a chain.

## `hekb.storage`

- `ProjectionBackend` — a `runtime_checkable` `Protocol` with one method:
  `write(profile: StorageProfile) -> None`.
- `InMemoryProjectionBackend` — a trivial in-memory implementation for
  tests/demos; exposes `.profiles: tuple[StorageProfile, ...]`.
- `to_storage_profile(relation: KnowledgeRelation) -> StorageProfile` —
  converts a committed morphism into its declarative storage profile.

## `hekb.runtime`

### `HEKBCoreRuntime`

```python
class HEKBCoreRuntime:
    def __init__(self, backend: ProjectionBackend) -> None: ...
```

| Method | Behavior |
|---|---|
| `category` (property) | The underlying `KnowledgeCategory`. |
| `ingest_object(concept)` | Admits a new object. |
| `ingest_morphism(relation)` | Validates axioms, then persists a `StorageProfile` for the accepted morphism. |
| `ingest_update(sigma_a, f, sigma_b, u_f)` | Validates the Homotopic Update Law before admitting/persisting `u_f`; raises `HomotopyViolation` and persists nothing on failure. |
| `export_epistemic_graph()` | Returns a frozen `EpistemicGraphSnapshot` of the current state. |
