# Changelog

All notable changes to HEKB are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
