# HEKB Architecture

## The algebraic model

HEKB models a knowledge graph as a category **K**, concretely realized as
the category of finite sets and functions (**Set**):

- An **object** of K (`Concept`) is a finite set of elements — `elements:
  frozenset[str]` — plus optional geometric metadata (`centroid`,
  `hessian`, `invariants`) that HEKB treats as opaque payload.
- A **morphism** of K (`KnowledgeRelation`) is a total function between
  two Concepts' element sets, represented as `mapping: dict[str, str]`.

Choosing Set as the concrete model is what makes every construction below
a real, terminating computation instead of an abstract existence claim:
Set is complete and cocomplete, so every limit/colimit HEKB needs
(products, pushouts, pullbacks) has a well-known, constructive
description.

## Category axioms

`KnowledgeCategory.add_object`/`add_morphism` enforce the axioms a
category requires before anything is admitted to K:

- Every object has an identity morphism (`KnowledgeCategory.identity`).
- Morphisms compose associatively (`compose`), and only when their
  boundaries match (`f.target == g.source`).
- A morphism's `mapping` must be **total** over its source's elements and
  land entirely within its target's elements — checked exactly, not
  approximately, via set equality/subset checks.

Violating any of these raises `CategoryAxiomViolation` and adds nothing
to K.

## The Homotopic Update Law

When an update `U` is proposed against an existing object `A` (producing
`U(A)`), HEKB requires the naturality square to commute:

```
        A --  f  --> B
        |            |
  sigma_A          sigma_B
        |            |
        v            v
       U(A) -- U(f) --> U(B)
```

i.e. `sigma_B . f == U(f) . sigma_A`. `KnowledgeCategory.verify_naturality`
checks this exactly (element-by-element mapping comparison) and raises
`HomotopyViolation` — never coerces or approximates — if it doesn't hold.
`HEKBCoreRuntime.ingest_update` calls this *before* admitting `U(f)` to K
or writing anything to storage: a broken update changes nothing.

## Universal constructions: pushout and pullback

- **Pushout** (`KnowledgeCategory.pushout`) of a span `A <--f-- C --g--> B`
  is constructed as the coequalizer of the disjoint union `A + B` under
  the relation `f(c) ~ g(c)` for every `c` in `C` — implemented with a
  union-find structure, the standard construction of pushouts in Set.
- **Pullback** (`KnowledgeCategory.pullback`) of a cospan `A --f--> C
  <--g-- B` is constructed directly as `{(a, b) : f(a) == g(b)}`.
- **The universal property is checked, not assumed.**
  `mediating_pushout_morphism` verifies that two candidate cocone
  morphisms `h_A`, `h_B` actually agree on every identified element
  before constructing the unique mediating morphism `u` — if they
  disagree, it raises `CategoryAxiomViolation` rather than silently
  picking one.

## The tensor / internal-hom adjunction

`KnowledgeCategory.tensor` models the monoidal product `A ⊗ B` as the
Cartesian product of the underlying sets. `internal_hom` models `[B, C]`
as the set of all total functions `B -> C`, each encoded as a canonical
string via `encode_function`. `curry`/`uncurry` implement the adjunction
isomorphism

```
Hom(A ⊗ B, C) ≅ Hom(A, [B, C])
```

as an executable round-trip: `uncurry(curry(f)) == f`, checked by
`tests/test_category.py::test_tensor_and_curry_uncurry_round_trip`.

## Storage ignorance

`hekb.storage.ProjectionBackend` is a `typing.Protocol` with a single
method, `write(profile: StorageProfile) -> None`. HEKB's core never
imports a database driver, issues SQL/CQL, or performs raw disk I/O —
persistence happens exclusively by constructing a `StorageProfile` (a
plain, inert dataclass) and handing it to whatever `ProjectionBackend` the
caller supplies.

This repository ships exactly one implementation of that protocol:
`InMemoryProjectionBackend`, a trivial in-memory list — sufficient for
tests and standalone demos, explicitly not a real store. Concrete
backends (relational, columnar, object storage, ...) are out of scope for
v1.0 by design: they belong in a separate package that depends on HEKB,
never the reverse.

This isn't just a convention — `tests/test_storage_ignorance_audit.py`
statically proves it via an AST scan of every module under `src/hekb`,
failing the test suite if any of them ever imports a known database
driver (`psycopg2`, `sqlalchemy`, `boto3`, `pymongo`, etc.).

## The runtime facade

`HEKBCoreRuntime` (`hekb.runtime`) owns one `KnowledgeCategory` and one
`ProjectionBackend`, and is the only object application code needs to
touch:

- `ingest_object` / `ingest_morphism` — admit new objects/morphisms,
  validating category axioms first; `ingest_morphism` also persists a
  `StorageProfile` for the accepted morphism.
- `ingest_update` — admit an update gated by the Homotopic Update Law;
  persists nothing if the naturality square doesn't commute.
- `export_epistemic_graph` — returns a frozen `EpistemicGraphSnapshot`
  (immutable tuples of the current objects/morphisms). Every call
  produces an independent value; later mutation of the runtime never
  retroactively changes a snapshot already handed out.

## What HEKB deliberately does not do

- It does not compute or interpret the `centroid`/`hessian`/`invariants`
  metadata on a `Concept` — those are carried through as opaque payload
  for whatever upstream or downstream system populates and consumes them.
- It does not implement a real storage backend, a transport/service
  layer, or orchestration of any kind.
- It does not observe, annotate, render, or make control decisions. See
  the README's "Design philosophy" section for how this fits into the
  broader HEXT ecosystem.
