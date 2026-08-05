# Changelog

All notable changes to HEKB are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added — EXP-HEKB006 v2.1.0 Reality Consensus Engine & real Human-vs-Human Ground Truth

`experiments/_reality_consensus.py` (the Reality Consensus Engine: a
Pullback Limit / K-way intersection of typed morphisms over any number of
real `_semantic_closure.SemanticClosure` values, plus Observer Bias
Index, leave-one-out robustness, blind-anonymization invariance, and a
false-convergence guard -- pure set arithmetic, no new retrieval, no
vector/embedding search), `experiments/_human_observers.py` (Phase 1's
real Human-vs-Human Ground Truth: 3 independently-authored real channels
-- `critique.md`, `wiki.md`, `catalog.json` -- already in EXP-HEKB005's
real corpus, re-partitioned into 3 separate real per-channel closures; no
new corpus fetched, no text generated), `experiments/_observer_registry.py`
(a unified registry spanning the real human-channel plane and the 7 named
LLM engines from EXP-HEKB006 v1.0.0's `_observer_adapter.py`, reused
unmodified), and `experiments/exp_hekb_006_reality_consensus.py` (the
v2.1.0 orchestrator: Phases 1-4 and Tests A-J, embedding v1.0.0's
`exp_hekb_006_cross_model.run()` output whole as
`cross_model_observer_plane_v1_0_0` rather than re-deriving its still-real
0/7-named-LLM-engine finding).

Per the v2.1.0 specification's own scope decision ("Observer APIs are
optional... execute all deterministic mechanisms... report only the
unavailable observer-dependent metrics as BLOCKED"), this addition is
measured, not blocked: all 9 real EXP-HEKB005 works have >= 2 real human
observers (6/9 have all 3), mean Consensus Reality Score 0.314, Phase 3's
abstract mechanism verification passes (Pullback Limit, OBI, leave-one-out
robustness, blind-anonymization invariance, and the false-convergence
guard all wired correctly), and Tests A/C/D/E/F/I/J pass on real data (36
real work-pairs disambiguated at 0.0% false convergence; real shared
`technique/sfumato`, `technique/camera_obscura`, `technique/impasto`
nodes found and correctly whitelisted, not merged). Tests B and H, and
Test G's specification-target >= 5-observer count, remain honestly
`BLOCKED` -- 0/7 named LLM engines are callable in this workspace, the
same real finding EXP-HEKB006 v1.0.0 already recorded. See
`docs/RFC_ALIGNMENT.md` ("EXP-HEKB006 v2.1.0: the Reality Consensus
Engine") and `experiments/EXP-HEKB006/report.md`'s "v2.1.0 Addendum" for
the full record, including two implementation bugs found and fixed during
verification (a size-sensitive OBI ranking, and an incomplete
false-convergence whitelist). `src/hekb` is unmodified.

### Added — EXP-HEKB006 v1.0.0 cross-model epistemic invariance (blocked on observer access)

`experiments/_observer_adapter.py` (the `ObserverAdapter` Protocol
boundary for the 7 named LLM engines -- Gemma, Qwen, Llama, Mistral,
Claude, GPT, Gemini -- plus a real, re-runnable `probe_observer_availability`
environment check), `experiments/_cross_model_runner.py` (per-observer
call orchestration with honest `NotImplementedError` reference stubs, no
fabricated text), and `experiments/_cross_model_compare.py` (the new
Cross-Model Comparison Engine: closure structure similarity, morphism
graph edit distance, pullback/pushout identity rate, proof path
alignment, invariant identity, completeness/latency variance -- all built
on EXP-HEKB002's `_semantic_closure.compute_closure`, reused unmodified).

A real environment probe found 0 of the 7 named observer engines callable
in this workspace (no local model runtime, no API credential for any of
them); per the specification's own "do not fabricate" instruction, every
one of the specification's 7 target metrics is honestly reported `NOT
MEASURED`, and the new comparison engine is instead verified against an
abstract, explicitly-labeled `MechanismTest_*` fixture (not real observer
output) that confirms it correctly discriminates a converged pair from a
divergent one. See `docs/RFC_ALIGNMENT.md` ("EXP-HEKB006: cross-model
epistemic invariance, blocked on observer access") and
`experiments/EXP-HEKB006/report.md` for the full record. `src/hekb` is
unmodified.

### Added — EXP-HEKB005 visual multi-modal ingestion (real corpus)

`experiments/_visual_corpus_fetch.py` (one-time real fetcher: Wikipedia,
Wikidata, Wikimedia Commons, plus real public-domain critique text from
Vasari, the 1911 Encyclopaedia Britannica, and Vincent van Gogh's own
letters), `experiments/_visual_observation_bundle.py` (visual Observation
Bundle data model), `experiments/_real_visual_extractors.py` (real
parsers over the cached corpus), `experiments/_visual_reconstruction.py`
(the Visual Observation Bundle Recovery Engine, reusing EXP-HEKB002's
`_semantic_closure.compute_closure` unmodified -- no vector or embedding
search).

Unlike EXP-HEKB004, this experiment's task required real data, and a real
9-work corpus (Leonardo da Vinci, Johannes Vermeer, Vincent van Gogh) was
fetched and ingested: 42 of 45 real observation points present (93%);
Observation Bundle Completeness, disambiguation (Test D), replay
determinism, and latency are real, measured results, all passing target.
`visual_convergence_score`, formal cross-subject technique-invariant
precision, and single-fragment-to-target resolution are honestly marked
not-measured/not-implemented, each requiring a real model this workspace
does not have. See `docs/RFC_ALIGNMENT.md` ("EXP-HEKB005: visual
multi-modal ingestion, real corpus") and
`experiments/EXP-HEKB005/report.md` for the full record. Pillow added as
a `.venv`-only gate dependency (not a declared `pyproject.toml`
dependency). `src/hekb` is unmodified.

### Added — EXP-HEKB004 multi-modal ingestion (design-stage only, implementation paused)

`experiments/_observation_bundle.py` (Observation Bundle data model and
typed-morphism vocabulary), `experiments/_multimodal_corpus.py` (the
9-work catalog and real corpus directory contract/discovery scan),
`experiments/_multimodal_extractors.py` (per-modality extractor
`Protocol` boundaries, no fabricated bodies), and
`experiments/_cross_modal_reconstruction.py` (the Cross-Modal
Reconstruction Engine, reusing EXP-HEKB002's `_semantic_closure.compute_closure`
unmodified — no vector or embedding search).

A real-filesystem audit found no real audio, score, or subtitle file, and
no composer/work-specific critique or theory text, for any of the 9
target works this experiment's specification names. Per the
specification's own "do not fabricate" instruction and explicit direction
from the requester, ingestion of the real 3x3 test matrix is **paused**;
none of the specification's 8 target metrics were measured. See
`docs/RFC_ALIGNMENT.md` ("EXP-HEKB004: multi-modal ingestion,
design-stage only") and `experiments/EXP-HEKB004/report.md` for the full
record, including the abstract, non-musical `mechanism_verification`
self-check that confirms the reconstruction engine's wiring is correct
independent of any real corpus. `src/hekb` is unmodified.

### Added — EXP archival: EXP-HEKB001, EXP-HEKB002, EXP-HEKB003 knowledge artifacts

`experiments/EXP-HEKB001/`, `experiments/EXP-HEKB002/`,
`experiments/EXP-HEKB003/` (new): each completed experiment's
specification, report, measured results, and quantitative metrics saved
as a formal, reproducible knowledge artifact
(`specification.md`, `report.md`, `results.json`, `metrics.json`,
`README.md`), independent of the implementation code under `experiments/`.

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
