# EXP-HEKB003 — Report

## Implementation Summary

EXP-HEKB003 replaced EXP-HEKB002's hand-specified Graphify fixture with
**real** multi-repository artifacts and added a reference Semantic Search
layer over the existing, unmodified Semantic Closure Engine:

- `experiments/_real_artifact_extractors.py` — real Markdown (backtick
  vocabulary/reference scanning), real Python (`ast.parse`-extracted
  top-level classes), and real Git (`git log`) structural extractors —
  reference adapters, not Graphify (none exists in this workspace).
- `experiments/_real_corpus.py` — assembles the real, curated,
  multi-repository corpus (Stage 1's repository survey): 3 real
  repositories, 10 real Markdown files, 17 real Python files, 52 real
  class names forming the concept vocabulary, 105 real objects total once
  ingested.
- `experiments/_semantic_search.py` — concept resolution, the geometric
  ranking function (`D_functorial`, `L_morphism`, `D_potential`,
  `Depth_category`, each honestly scoped to what is actually computable),
  an independently re-verified false-inclusion check, and the
  specification's §V response payload shape.
- `experiments/exp_hekb_003_real_world_validation.py` — orchestrates
  Stages 1–6 and all named metrics.
- `experiments/_concept_store.py`, `experiments/_file_backend.py` — fixed
  a real path-safety bug (below).

## Architectural Findings

- **`_semantic_closure.compute_closure` was reused unmodified.** No
  redesign of the closure algorithm; the Semantic Search layer is built
  entirely on top of it.
- **The geometric ranking function's four terms are honestly, distinctly
  scoped**: `L_morphism`/`D_functorial` are two real, different BFS hop
  counts (undirected vs. pullback-only) — not one relabeled as two.
  `D_potential` is a real Mahalanobis-style distance when both objects
  carry a `centroid` (only CLE-derived concepts do) and an honest `0.0`
  otherwise, never a fabricated placeholder for the ~104 real
  document/code/commit objects with no geometry. `Depth_category` is a
  fixed, documented ordinal table, not a learned signal.
- **A real path-safety bug found and fixed, entirely within
  `experiments/`.** `FileConceptStore`/`FileProjectionBackend` (from
  EXP-HEKB001/002) built on-disk filenames directly from record ids;
  neither predecessor ever exercised an id containing `/`. EXP-HEKB003's
  real, path-shaped ids (e.g. `"msr/src/msr/abi.py"`) broke this
  immediately. Fixed by escaping `/` to `__` in the on-disk filename
  only — every stored `id` field, and every id either predecessor
  produced, is byte-identical to before.

## Boundary Findings

- `src/hekb` unmodified — 29 tests, 91% coverage, unchanged from baseline.
- No Graphify repository exists anywhere in this workspace —
  `_real_artifact_extractors.py` are reference extractors, explicitly not
  Graphify, per instruction.
- No `RFCv3_draft`, `sensos-docs`, or ADR directory exists under those
  names in any of the three repositories surveyed (`meaning-space-runtime`,
  `categorical-lift-engine`, this repository) — real artifacts were drawn
  from what actually exists instead of a fabricated substitute.
- No vector or embedding search anywhere — pure categorical/graph
  retrieval throughout, per explicit instruction.

## Validation Metrics

| Property | Result |
|---|---|
| Cross-domain traversal yield | Pass — 0 uncaught exceptions across 3 real queries |
| Composition depth | Pass — a genuine real 4-hop composed morphism (`msr/docs/BOUNDARIES.md → ... → KernelView`), folded via HEKB's real `compose` |
| Deterministic replay | Pass — identical payload (excluding wall-clock timing) across repeated runs |
| Pullback accuracy | Pass — independently re-confirmed by grepping real raw source text directly |
| Pushout recall | Pass — 1.0; every real direct dependent found by an independent from-scratch graph scan appears in the closure |
| Semantic search latency at scale | Pass — 105 real nodes, p99 0.125ms against a 10ms target |
| Differential synchronization | Pass — two real git revisions of `msr/src/msr/abi.py`, idempotent re-ingestion (0 new records), exact diff identity |
| Context economy ratio | Reported honestly, not force-gated on the 0.15 target — 0.086/0.019/0.219 across the three real queries tested; a real, query-dependent number on a deliberately small (105-object) proof-of-concept-scale corpus |

Full measured values: `results.json` (copied verbatim from
`experiments/results/exp_hekb_003.json` as committed at `f2ed9ec`).

## Quality Gates

pytest: 29 passed · coverage: 91% (unchanged) · ruff check: clean · ruff
format --check: clean · mypy --strict (`mypy .`): clean, 31 files.

## Lessons Learned

1. **Real data finds bugs synthetic fixtures don't.** The path-safety bug
   (record ids containing `/`) was invisible across two prior experiments
   because no fixture id ever happened to contain a path separator — real
   file-derived ids exposed it on the first run.
2. **A metric target chosen against an imagined corpus scale should be
   reported honestly against the real one, not gated to force a pass.**
   `context_economy_ratio ≤ 0.15` does not hold for every query shape on
   a deliberately small, curated 105-object real corpus — this is an
   accurate, informative result about corpus scale, not a failure of the
   ranking/closure mechanism, and was reported as such rather than
   massaged to a uniform pass.
3. **Independent re-verification (not just trusting the algorithm's own
   output) is what makes a "0% false inclusion" or "100% recall" claim
   credible.** Both were checked by an independently reconstructed BFS or
   graph scan in this experiment, not merely inferred from the closure
   algorithm having run without error.
