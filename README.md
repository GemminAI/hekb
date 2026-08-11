# HEKB

[![CI](https://github.com/gemminai/hekb/actions/workflows/python.yml/badge.svg)](https://github.com/gemminai/hekb/actions/workflows/python.yml)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)

**HEKB is the knowledge-storage layer of the HEXT ecosystem.**

It is a storage-ignorant, category-theoretic knowledge substrate: a small,
dependency-free algebraic core that models a knowledge graph as a
mathematical category — with real, checked category axioms, universal
constructions (pushout, pullback), and a monoidal adjunction — instead of
an ad-hoc graph data structure.

HEKB is not a database, not a service, and not a framework. It is a
library you embed, whose correctness guarantees come from category
theory rather than from application-level validation code.

---

## Fresh install status

Verified by cloning this repository into a clean, isolated directory
(no pre-existing HEKB workspace, database, cache, or virtual
environment reused):

| Step | Result |
|---|---|
| `git clone` + `uv sync` | **PASS** |
| `uv run pytest` | **PASS** (29 tests, includes the storage-ignorance audit) |
| `uv run ruff check .` | **PASS** |
| `uv run mypy .` | **FAIL** — `src/hekb` itself is clean; the failures are all in `experiments/`, which imports other, separately-installed repositories (`numpy`, `PIL`, `requests`, and the unrelated `cle`/`msr` packages) that are not part of this repository's own dependencies. This matches this repository's own current CI status on `main` (also failing, for the same reason) — it is a pre-existing upstream state, not something introduced by a fresh install. |
| Empty-state health check (`HEKBCoreRuntime(InMemoryProjectionBackend())`, then `export_epistemic_graph()`) | **PASS** — `EpistemicGraphSnapshot(vertices=(), edges=())`, no leftover data |
| Read/write test (the Quick start example below) | **PASS** — `2 1`, matching this README |

**Not shipped, and therefore not verified by this check**: any
persistent storage backend. Only `InMemoryProjectionBackend` (process-
local, non-persistent) is part of the installed package — see
"Repository boundaries" below. `experiments/` contains a private,
non-shipped `FileProjectionBackend`/`FileConceptStore` used to validate
deterministic-replay/idempotent-commit properties in isolation, but it
depends on other repositories not installed by `uv sync`, and is not
part of the `hekb` package a `pip install hekb` / `uv add hekb` user
receives.

---

## What HEKB is

Concretely, HEKB models a knowledge category **K** as the category of
finite sets and functions (**Set**), which is both complete and
cocomplete with well-known constructive limits and colimits. That choice
is what turns every operation below from a metaphor into a real,
checkable computation:

- **Objects** (`Concept`) are finite sets of elements, optionally carrying
  geometric metadata (a centroid, a Hessian, arbitrary invariants) that
  HEKB itself never computes or interprets — it only carries that payload
  through.
- **Morphisms** (`KnowledgeRelation`) are total functions between two
  Concepts' element sets. A `KnowledgeCategory` enforces totality and
  codomain-membership on every morphism it admits — an incoherent
  morphism is rejected before it ever exists inside K.
- **Updates are checked, not trusted.** The Homotopic Update Law verifies
  that a proposed update's naturality square actually commutes
  (`sigma_B . f == U(f) . sigma_A`) before it's accepted. A broken update
  raises `HomotopyViolation` and changes nothing.
- **Pushouts and pullbacks are executed on demand**, as real
  union-find/filtering computations in Set — not asserted as abstract
  equations. `mediating_pushout_morphism` constructively verifies the
  universal property's existence-and-uniqueness claim, rather than
  assuming it.
- **The tensor / internal-hom adjunction is an executable round-trip.**
  `curry`/`uncurry` witness `Hom(A⊗B, C) ≅ Hom(A, [B,C])` concretely, on
  finite examples, checked by the test suite.
- **Persistence is a boundary HEKB defines but never crosses.** The
  algebraic core never imports a database driver; it only ever emits a
  `StorageProfile` to a `ProjectionBackend`. This is enforced, not just
  documented — a static AST audit in the test suite fails the build if
  any module under `hekb` imports a real database library.

## Architecture

```
        Application code
              │
              │  ingest_object() / ingest_morphism() / ingest_update()
              ▼
      HEKBCoreRuntime            (hekb.runtime)
        │            │
        │            └── validates via ──▶  KnowledgeCategory   (hekb.category)
        │                                    - category axioms
        │                                    - Homotopic Update Law
        │                                    - pushout / pullback
        │                                    - tensor / internal-hom
        │
        └── on success, writes ──▶  ProjectionBackend            (hekb.storage)
                                       - a Protocol; no concrete
                                         implementation ships in v1.0
                                         except InMemoryProjectionBackend
                                         (tests/demos only)
        │
        └── export_epistemic_graph() ──▶  EpistemicGraphSnapshot (hekb.models)
                                           a frozen, immutable value —
                                           the only thing downstream
                                           consumers ever see
```

Every write path validates category axioms **before** touching storage.
An axiom violation or a broken naturality square persists nothing — HEKB
never lets an inconsistent state reach a backend, real or fake.

## Design philosophy

HEKB is one layer in a larger design where responsibilities are
deliberately not blurred:

> HEXT defines. **HEKB stores.** SensOS observes. NVS-Kernel decides. LLMs render.

HEKB's job is exactly "stores" — durably and coherently representing a
knowledge graph, with the category-theoretic guarantees above standing in
for the validation logic a less rigorous store would need to hand-write
and hope is complete. HEKB does not:

- observe the world, or ingest raw sensor/text/model data (that's an
  observation layer's job, upstream of HEKB);
- compute geometry, curvature, or potential fields over the graph it
  stores (that's a downstream geometry-compilation layer's job — HEKB
  only carries opaque `centroid`/`hessian`/`invariants` metadata through,
  never computing it);
- make control decisions or render language (those are other layers
  entirely).

This is why HEKB v1.0 has **zero runtime dependencies**: it doesn't need
a web framework, a database driver, or an ML library to be correct. Every
guarantee it makes is checkable with nothing but the Python standard
library and a test suite.

## Repository boundaries

This repository (v1.0) contains **only the knowledge layer**:

| In scope | Out of scope (later phases / other repositories) |
|---|---|
| `KnowledgeCategory`, `Concept`, `KnowledgeRelation` | Observation ingestion, semantic annotation |
| `EpistemicGraphSnapshot`, `HEKBCoreRuntime` | Geometry/curvature/potential-field compilation |
| Homotopic Update Law, pushout, pullback, tensor/internal-hom | Controller / decision logic |
| `ProjectionBackend` interface + `InMemoryProjectionBackend` | Concrete storage backends (PostgreSQL, ScyllaDB, MinIO, ...) |
| Unit tests, API docs, developer docs | Runtime orchestration, service/HTTP layers, Docker |
| | Model Context Protocol (MCP) integration |
| | LLM integration / rendering |

If you need any of the "out of scope" items, they belong to a later HEKB
phase or to a different component of the HEXT ecosystem (SensOS,
NVS-Kernel, or HEXT itself) — not to this repository.

**SensOS integration: not yet implemented, anywhere.** As of this
writing, no code in this repository, in `semantic_annotator`
(`RuntimeBridge`/`LLMAnnotator`), or in the SensOS Linux Installer
imports or connects to `hekb`. A separate, unrelated experiment
(`sensos_integration.hekb_runtime` in `nvs-platform-runtime`) exists,
but it wires together that monorepo's own internal `exp7100`/`exp7500`
modules — not this package — and does not touch `semantic_annotator`
either. Installing HEKB today gives you a standalone library only; it
does not make HEKB reachable from a SensOS installation.

## Installation

Requires Python 3.12+.

**From source (works today):**

```bash
git clone https://github.com/gemminai/hekb.git
cd hekb
uv sync            # with uv, or:
pip install -e .   # with pip
```

**From PyPI (once published):**

```bash
uv add hekb
# or: pip install hekb
```

HEKB is not yet published to PyPI — use the source install above until a
release is published there.

## Quick start

```python
from hekb import Concept, HEKBCoreRuntime, InMemoryProjectionBackend, KnowledgeRelation

runtime = HEKBCoreRuntime(InMemoryProjectionBackend())

runtime.ingest_object(Concept(id="cat", elements=frozenset({"whiskers", "tail", "purr"})))
runtime.ingest_object(Concept(id="animal", elements=frozenset({"legs", "tail", "fur"})))

runtime.ingest_morphism(
    KnowledgeRelation(
        id="cat_is_a_animal",
        source="cat",
        target="animal",
        mapping={"whiskers": "fur", "tail": "tail", "purr": "legs"},
    )
)

snapshot = runtime.export_epistemic_graph()
print(len(snapshot.vertices), len(snapshot.edges))  # 2 1
```

An axiom-violating morphism is rejected before it ever touches storage:

```python
from hekb.category import CategoryAxiomViolation

try:
    runtime.ingest_morphism(
        KnowledgeRelation(id="bad", source="cat", target="animal", mapping={"whiskers": "fur"})
    )  # not total over cat's elements
except CategoryAxiomViolation as exc:
    print(exc)  # "morphism 'bad' is not total over its source's elements: ..."
```

See [`examples/basic_usage.py`](examples/basic_usage.py) for a longer,
runnable walkthrough including pushout and the Homotopic Update Law.

## API overview

| Module | Exports |
|---|---|
| `hekb.models` | `Concept`, `KnowledgeRelation`, `StorageProfile`, `EpistemicGraphSnapshot` |
| `hekb.category` | `KnowledgeCategory`, `CategoryAxiomViolation`, `HomotopyViolation`, `compose_all`, pair/function encoding helpers |
| `hekb.storage` | `ProjectionBackend` (Protocol), `InMemoryProjectionBackend`, `to_storage_profile` |
| `hekb.runtime` | `HEKBCoreRuntime` |

All of the above are re-exported from the top-level `hekb` package. See
[`docs/api.md`](docs/api.md) for the full reference and
[`docs/architecture.md`](docs/architecture.md) for the underlying
algebraic model in more depth.

## Development

```bash
uv run pytest              # tests, including the storage-ignorance audit
uv run ruff check .        # lint
uv run mypy .              # type check
```

`mypy .` currently reports errors under `experiments/` (missing stubs
for other repositories' packages, not part of this repo's own
dependencies) — see "Fresh install status" above. `src/hekb` itself is
mypy-clean.

## License

Apache License 2.0 — see [`LICENSE`](LICENSE) and [`NOTICE`](NOTICE).
