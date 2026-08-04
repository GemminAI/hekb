# Changelog

All notable changes to HEKB are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added — EXP-HEKB003 real-world cross-domain semantic search & closure

Replaces EXP-HEKB002's hand-specified Graphify fixture with **real**
multi-repository artifacts (`meaning-space-runtime`,
`categorical-lift-engine`, this repository: real Markdown, real Python via
`ast.parse`, real `git log`), and adds a reference Semantic Search layer
over the existing, unmodified Semantic Closure Engine. No vector or
embedding search anywhere; no Graphify or homotopy algorithm invented. See
`docs/RFC_ALIGNMENT.md` ("EXP-HEKB003: real-world cross-domain semantic
search & closure") for the full record, including a real path-safety bug
found and fixed in `experiments/`-only infrastructure.

- `experiments/_real_artifact_extractors.py` (new): real Markdown/Python/Git
  structural extractors — reference adapters, not Graphify.
- `experiments/_real_corpus.py` (new): assembles the real, curated,
  multi-repository corpus (Stage 1's repository survey); 105 real objects,
  52 real classes forming the concept vocabulary.
- `experiments/_semantic_search.py` (new): concept resolution, the
  geometric ranking function (`D_functorial`, `L_morphism`, `D_potential`,
  `Depth_category`, each honestly scoped to what's actually computable),
  an independently-reverified false-inclusion check, and the §V-shaped
  response payload.
- `experiments/exp_hekb_003_real_world_validation.py` (new): orchestrates
  Stages 1–6, all metrics pass — `experiments/results/exp_hekb_003.json`
  (`"pass": true`), including a genuine real 4-hop composed morphism and
  100% independently-verified pushout recall.
- `experiments/_concept_store.py`, `experiments/_file_backend.py`
  (fixed): on-disk filenames now escape `/` — EXP-HEKB001/002 never
  exercised a path-shaped record id; EXP-HEKB003's real file-path ids
  did. Stored `id` fields, and every existing id, are unchanged.

### Added — EXP-HEKB002 closed-loop end-to-end verification

Validates the full loop MM/MSR -> CLE -> HEKB storage -> Semantic Closure
query -> MCP -> MSR re-injection, using real, unmodified
`meaning-space-runtime`/`categorical-lift-engine` production code where it
exists, and honest reference fixtures where it doesn't (Graphify, MCP
transport). `src/hekb` is unmodified. See `docs/RFC_ALIGNMENT.md`
("EXP-HEKB002: closed-loop end-to-end verification") for the full record,
including the gate-dependency note, scope decisions, a new CLE-ABI
adapter, and a fixture bug (an accidental 2-cycle) found and fixed during
this work.

- `experiments/_msr_cle_pipeline.py` (new): a real `MeaningSpaceRuntime` +
  `CategoricalLiftEngine` (its own `cle.reference` strategies) produce one
  genuine `StabilizedTrajectory` -> `Concept`.
- `experiments/_cle_hekb_adapter.py` (new): `cle.abi.outputs.Concept` ->
  `hekb.models.Concept` — no such adapter existed anywhere in the
  workspace before this.
- `experiments/_concept_store.py` (new): `FileConceptStore`, extending
  EXP-HEKB001's `FileProjectionBackend` pattern to `Concept`s (which
  `HEKBCoreRuntime.ingest_object` never persists).
- `experiments/_graphify_reference.py` (new): a deterministic
  `PropertyGraph` fixture — explicitly not production Graphify.
- `experiments/_functorial_graph_adapter.py` (new): a real, checked
  `PropertyGraph -> C_HEKB` functor, including a functoriality-preservation
  check against HEKB's real `compose`.
- `experiments/_semantic_closure.py` (new): the Semantic Closure Engine —
  pure categorical retrieval (no vector/embedding search), computing a
  deterministic, verified-minimal self-contained subcategory with pullback
  root / pushout wavefront navigation.
- `experiments/_mcp_reference.py` (new): an in-process reference MCP query
  interface (not a real network MCP server) returning the EXP-HEKB002 §V
  response shape.
- `experiments/exp_hekb_002_closed_loop.py` (new): orchestrates Phases
  1–5, measures all ten metrics the specification and its implementation
  instructions name. All pass — `experiments/results/exp_hekb_002.json`
  (`"pass": true`).

### Added — EXP-HEKB001 persistence & lineage validation

Validates `HEKBCoreRuntime` against a real, file-based `ProjectionBackend`
instead of `InMemoryProjectionBackend` — no `src/hekb` code changed. See
`docs/RFC_ALIGNMENT.md` for the full record, including two corrections to
the commissioning specification (a boundary-model mismatch around category
theory, and a Graphify-integration scope correction) and one open
architectural question (the `StorageProfile` fidelity gap) left
undecided.

- `experiments/_file_backend.py` (new): `FileProjectionBackend` — a real,
  deterministic, SHA-256-content-hashed `ProjectionBackend` implementation.
  Lives outside `src/hekb`, depends on `hekb`, never the reverse — the
  extension point `docs/architecture.md` already names. Writes plain JSON
  via the standard library only; no database driver.
- `experiments/_lineage_fixture.py` (new): the RFC-MM001/RFC-MSR01
  defines/consumes/provenance example from EXP-HEKB001 itself, built as
  real `Concept`/`KnowledgeRelation` values — not a Graphify stand-in.
- `experiments/exp_hekb_001_persistence_validation.py` (new): validates
  round-trip identity, deterministic replay, idempotent commit, duplicate
  detection, immutability, recovery, lineage composition, and
  synthetic-scale lookup latency (500 records, p95 0.77ms against a <5ms
  target). Run against the real path this repository lives at
  (`/media/psf/SSD1TB/HEKBv2`), via a dedicated, gitignored
  `experiments/_hekb_store/` scratch subdirectory. All pass —
  `experiments/results/exp_hekb_001.json` (`"pass": true`).
- `docs/RFC_ALIGNMENT.md` (new).
- `pyproject.toml`: `experiments` added to `[tool.ruff] src`, matching
  `meaning-space-runtime`'s/`categorical-lift-engine`'s convention of
  linting their own `experiments/`.
- Graphify integration (EXP-HEKB001 Stage 3) is explicitly **not**
  implemented or stubbed: no Graphify repository exists in this workspace,
  and no `ProducerLike`/parsing interface was invented to stand in for it.
  Recorded as an external-dependency milestone in `docs/RFC_ALIGNMENT.md`.

### Not changed

- No API changes. `src/hekb` is unmodified: 29 tests, 91% coverage
  (unchanged from baseline; no `fail_under` gate), ruff clean, `mypy
  --strict` clean.
- `tests/test_storage_ignorance_audit.py` still passes unmodified — this
  work adds a concrete backend outside `src/hekb`, not inside it.

## [1.0.1] - 2026-07-29

Recovery release. `v1.0.0` was tagged against a repository bootstrap
commit (`LICENSE` + `README.md` only, from the pre-release scaffolding
step) before the actual v1.0 source tree had been pushed to `main`.
This release corrects that: the intended implementation, previously
only reachable via the `recovery/hekb-v1-refresh` branch, is now
merged into `main` and is what `v1.0.1` points to.

### Fixed

- Canonical repository restored: `main` now contains the complete
  HEKB v1.0 source tree (`src/`, `tests/`, `docs/`, `examples/`,
  `pyproject.toml`) instead of the stray bootstrap commit.
- GitHub Actions restored: `.github/workflows/python.yml` (ruff, mypy
  strict, pytest across Python 3.12/3.13 via `uv`), which had been
  temporarily removed to work around a token missing the `workflow`
  OAuth scope.
- Packaging and repository history corrected; no functional regressions
  from `v1.0.0`'s intended scope.

### Not changed

- No API changes.
- No behavioral changes to the category-theoretic core, storage
  boundary, or runtime facade.

## [1.0.0] - 2026-07-29

First public OSS release of HEKB: the knowledge layer of the HEXT
ecosystem, standing on its own as an independent project.

### Added

- `hekb.category.KnowledgeCategory` — a mutable registry of `Concept`
  objects and `KnowledgeRelation` morphisms forming the knowledge
  category K, modeled concretely as the category of finite sets and
  functions (Set).
- Category axioms: identity morphisms, composition, and a total-function
  check on every morphism added to the category.
- The Homotopic Update Law: `verify_naturality` checks that a proposed
  update's naturality square commutes, raising `HomotopyViolation` — never
  silently coercing — if it doesn't.
- Pushouts and pullbacks, constructed directly in Set (a union-find
  coequalizer for pushout, direct filtering for pullback), with
  `mediating_pushout_morphism` constructively verifying the universal
  property's existence-and-uniqueness claim.
- The tensor / internal-hom / curry / uncurry adjunction
  `Hom(A⊗B, C) ≅ Hom(A, [B,C])`, demonstrated as an executable round-trip.
- `hekb.storage.ProjectionBackend` — the storage-ignorance boundary — plus
  `InMemoryProjectionBackend`, a test/demo fake. No concrete database
  backend is included in v1.0 by design.
- `hekb.runtime.HEKBCoreRuntime` — the facade wiring the algebraic core to
  a storage boundary, validating category axioms before any write ever
  reaches the backend.
- `hekb.runtime.HEKBCoreRuntime.export_epistemic_graph` — a frozen,
  immutable `EpistemicGraphSnapshot` export of the current knowledge graph.
- A complete unit test suite, including a static AST-based audit proving
  no module under `hekb` imports a database driver.
- API documentation, developer documentation, and a runnable example.

### Scope notes

This release contains only the knowledge layer. Observation, semantic
annotation, geometry/curvature/potential-field compilation, controller
logic, runtime orchestration, concrete storage backends, MCP integration,
and LLM integration are all out of scope for v1.0 — see `README.md`
"Repository boundaries" for where each of those belongs.
