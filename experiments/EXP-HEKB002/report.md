# EXP-HEKB002 — Report

## Implementation Summary

EXP-HEKB002 validated the full closed loop the specification names, using
**real, unmodified production code** wherever it exists, and explicitly
labeled reference fixtures everywhere it doesn't:

- **Real**: `meaning-space-runtime` (`MeaningSpaceRuntime`, `FieldPrior`,
  `msr.adapters.hekb.field_prior_from_concepts`) and
  `categorical-lift-engine` (`CategoricalLiftEngine` + its own
  `cle.reference` strategies) — installed editable into this repository's
  `.venv`, experiments-only, mirroring `meaning-space-runtime`'s own
  `nvs-kernel` gate-dependency precedent.
- **New, in `experiments/`** (`src/hekb` untouched throughout):
  `_msr_cle_pipeline.py` (real MSR+CLE pipeline producing one genuine
  `StabilizedTrajectory` → `Concept`), `_cle_hekb_adapter.py` (a
  genuinely-missing `cle.abi.outputs.Concept` ↔ `hekb.models.Concept`
  bridge), `_concept_store.py` (extends EXP-HEKB001's file-backend pattern
  to `Concept`s, which `HEKBCoreRuntime.ingest_object` never persists),
  `_graphify_reference.py` (a deterministic fixture, explicitly not
  production Graphify), `_functorial_graph_adapter.py` (a real, checked
  `PropertyGraph -> C_HEKB` functor), `_semantic_closure.py` (the Semantic
  Closure Engine — pure categorical retrieval, no vector/embedding
  search), `_mcp_reference.py` (an in-process reference query interface,
  not a network MCP server), and the orchestrator
  `exp_hekb_002_closed_loop.py`.

## Architectural Findings

- **A real adapter gap, bridged.** No code anywhere converted
  `cle.abi.outputs.Concept` ↔ `hekb.models.Concept` before this work.
  Built as a reference bridge; geometric fields (`centroid`/`hessian`/
  `invariants`) transfer exactly since both ABIs already agree on shape —
  this is what makes Phase 5 (closed-loop reuse) possible at all.
- **A fixture-authoring bug, not a HEKB bug.** An early version of the
  Graphify fixture encoded "RFC-MM001 defines MeaningMeasurement" and its
  exact inverse ("MeaningMeasurement exists in the context of RFC-MM001")
  as two opposite-direction edges between the same two nodes — a 2-cycle.
  `_semantic_closure.py`'s pullback/pushout root detection assumed
  acyclicity and either infinite-looped or returned empty root sets. Fixed
  in the fixture (one direction only, DAG); cycle-guards were kept in
  `_semantic_closure.py` regardless, since `KnowledgeCategory` itself is
  not required to be acyclic in general.
- **§V's `homotopy_hash`/`betti_numbers` were omitted, not fabricated** —
  `categorical-lift-engine` implements no homotopy algorithm
  (`cle.homotopy` is an interface only). A real `content_sha256` (the same
  convention EXP-HEKB001 established) stands in.

## Boundary Findings

- `src/hekb` unmodified — 29 tests, 91% coverage, unchanged from baseline.
- Architectural boundaries held throughout: Graphify stayed a structural
  producer (fixture, no parser invented), the Functorial Graph Adapter is
  a real checked lift, the Semantic Closure Engine is pure categorical
  retrieval, MCP stayed a query interface (no server), and HEKB remained
  storage-ignorant.
- EXP-HEKB001's `StorageProfile` fidelity gap (`ingest_object` never
  persists `Concept`s) still stands, unfixed; extended via harness-level
  `FileConceptStore` rather than touching production code.

## Validation Metrics

| Property | Result |
|---|---|
| End-to-end yield | Pass — 0 uncaught exceptions across the full Phase 1–5 run |
| Persistence (identity/replay/idempotency/duplication) | Pass — both `Concept`s and `KnowledgeRelation`s |
| Dual-source cross-reference alignment | Pass — real composed morphism spans both ingestion paths |
| Semantic Closure correctness | Pass — deterministic, verified-minimal, correct pullback root, functoriality verified against a hand-computed expected composition |
| MCP query latency | Pass — 200 samples, p99 0.041ms against a 5ms target |
| Closed-loop re-injection | Pass — a `Concept` reloaded from disk drives a fresh `FieldPrior`; a perturbed observation genuinely re-stabilizes into the recovered basin |

Full measured values: `results.json` (copied verbatim from
`experiments/results/exp_hekb_002.json` as committed at `1799c32`).

## Quality Gates

pytest: 29 passed · coverage: 91% (unchanged) · ruff check: clean · ruff
format --check: clean · mypy --strict (`mypy .`): clean, 27 files.

## Lessons Learned

1. **Reuse validated production code across repositories when it's
   already real and tested**, rather than re-fabricating a fixture for
   something that genuinely exists (`meaning-space-runtime`/
   `categorical-lift-engine`'s own reference strategies). This produced a
   materially stronger experiment than EXP-HEKB001's all-fixture approach.
2. **A modeling mistake (the fixture 2-cycle) is easiest to catch when the
   algorithm under test is exercised against a graph with real structural
   variety**, not a trivially small hand-checked example — this
   motivated moving to real-world artifacts in EXP-HEKB003.
3. **"Closed-loop reuse" should be proven functionally, not just by
   object equality.** Round-tripping a `Concept` through storage is a
   weaker claim than proving a fresh `MeaningSpaceRuntime`, built only
   from the *reloaded* object, actually recovers a perturbed trajectory
   into the right basin — the latter is what this experiment measured.
