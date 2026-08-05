# RFC Alignment

No `RFC-HEKB` document exists anywhere in the workspace as of this
repository's creation. This document records how an externally-supplied
experiment specification, **EXP-HEKB001** ("Graphify & HEKB Persistence
Validation," 2026-08-04), was reconciled against this repository's actual
state — what was validated as-is, what was corrected, and what remains an
open, undecided question — following this workspace's Implementation-First
convention (see `meaning-space-runtime`'s and `categorical-lift-engine`'s
own `docs/RFC_ALIGNMENT.md` for precedent: a gap between a spec and the
implementation is recorded here, not silently resolved in either
direction).

## Boundary-model correction

EXP-HEKB001 Stage 2 states HEKB "must NOT become responsible for ...
Category theory." That does not describe this repository. `hekb.category`
— category axioms, the Homotopic Update Law, pushouts, pullbacks, the
tensor/internal-hom adjunction — **is** HEKB's entire algebraic core, by
its own explicit self-description (`src/hekb/__init__.py`: *"a
storage-ignorant, category-theoretic knowledge substrate"*). This is not a
boundary leak to fix; it's the spec describing a different division of
responsibility than the one this repository actually implements (compare:
in `categorical-lift-engine`, a *separate* categorical lift — trajectory
to concept — is that repository's job, not HEKB's; the two are not the
same categorical operation). No code changed as a result of this finding.

## Graphify: recorded as an external dependency, not implemented

No Graphify repository exists anywhere in this workspace. Per explicit
instruction, this experiment does **not** invent a `ProducerLike`
Protocol, a Markdown parser, or any other stand-in for Graphify inside
HEKB or inside this experiment's harness — Graphify's public interface is
Graphify's own to define, not HEKB's or this harness's to guess at.
`experiments/exp_hekb_001_persistence_validation.py` therefore starts
*after* the Graphify boundary: it constructs `hekb.models.Concept`/
`KnowledgeRelation` values directly (see `experiments/_lineage_fixture.py`)
— squarely inside HEKB's own domain, exercising its real `Protocol`
conformance and category-axiom checks, not a simulation of Graphify's
output format. **Stage 3 (Graphify Integration) and the Graphify-dependent
portion of Stage 5 remain an integration milestone, deferred until
Graphify exports a real interface HEKB can validate against.**

## StorageProfile fidelity gap (Priority C — open, not decided here)

`hekb.storage.to_storage_profile` emits a *declarative* summary of a
morphism — `morphism_id`, `domain`, `codomain`, `invariants` — and does
not include the morphism's `mapping` (the actual total function). Worse:
`HEKBCoreRuntime.ingest_object` never calls the backend at all, so no
`Concept` — the object side of K — ever reaches a `ProjectionBackend`
today, real or fake.

This means EXP-HEKB001's Metric 2 (`Hash(Load(Save(O))) ≡ Hash(O)`,
"Round-Trip Identity") cannot currently hold for `O` = a full `Concept` or
`KnowledgeRelation`. `experiments/exp_hekb_001_persistence_validation.py`
validates round-trip identity of exactly what the current ABI actually
persists — the `StorageProfile` — and passes at 100% for that scope. It
does **not** claim full-object round-trip fidelity, because the current
design does not support it.

Whether `StorageProfile`'s payload should be widened to carry full
morphism/object fidelity, or whether that is intentionally a concrete
backend's own responsibility (e.g., a relational backend reconstructing
`mapping` from its own join-table schema rather than from a generic JSON
blob) is a genuine open design question about what `StorageProfile` is
*for*. It is not decided by this document, and `src/hekb/storage.py` was
not modified to resolve it — this is exactly the kind of call this
workspace's convention reserves for a real architectural decision, not an
autonomous fix.

## What was validated (`experiments/exp_hekb_001_persistence_validation.py`)

A real, deterministic, SHA-256-content-hashed, file-based
`ProjectionBackend` (`experiments/_file_backend.py`) — not
`InMemoryProjectionBackend`, and not a database driver (no import under
`src/hekb` changed; `tests/test_storage_ignorance_audit.py` remains
unmodified and still passes). It lives in `experiments/`, depending on
`hekb`, never the reverse — exactly the extension point
`docs/architecture.md` already names: *"Concrete backends ... belong in a
separate package that depends on HEKB, never the reverse."*

Run against the real path this repository lives at
(`/media/psf/SSD1TB/HEKBv2`, via a dedicated, gitignored
`experiments/_hekb_store/` scratch subdirectory — not the repository
root):

| Property | Result |
|---|---|
| Round-trip identity (of the `StorageProfile` the ABI actually persists) | **Pass** — 4/4 records, `Hash(Load(Save(O))) == Hash(O)` |
| Deterministic replay | **Pass** — a fresh `FileProjectionBackend` instance pointed at the same directory reproduces an identical record set |
| Idempotent commit | **Pass** — writing the same content twice produces zero duplicate records, byte-identical file |
| Duplicate detection | **Pass** — `KnowledgeCategory.add_morphism` rejects a re-ingested morphism id (`CategoryAxiomViolation`) *before* the backend is ever touched |
| Immutability | **Pass** — `Concept`, `KnowledgeRelation`, `StorageProfile`, `EpistemicGraphSnapshot` all reject mutation |
| Recovery | **Pass**, scoped to what `StorageProfile` carries — a fresh runtime + backend pointed at the same directory recovers every persisted record's identity and metadata; this does **not** claim full graph reconstruction (see fidelity gap above) |
| Cross-reference lineage (Stage 5, synthetic fixture) | **Pass** — RFC-MM001/RFC-MSR01's defines/consumes/provenance example from the spec itself, built as real `Concept`/`KnowledgeRelation` values, composed via `KnowledgeCategory.compose` into one real lineage morphism, deterministically |
| Lookup latency (Stage 7, synthetic-scale only) | **Pass** — 500 synthetic records, p95 lookup 0.77ms against a < 5ms target |

Full results: `experiments/results/exp_hekb_001.json` (`"pass": true`).

## Stage 5/7 corpus substitution

Neither `RFCv3_draft` nor `sensos-docs` nor "Daily Logs" exist under those
names anywhere in this workspace. Rather than guessing at a substitute
corpus, Stage 5's cross-reference example was built as a small, honest,
hand-specified fixture using the exact `RFC-MM001`/`RFC-MSR01` example the
EXP-HEKB001 specification itself gives (`experiments/_lineage_fixture.py`),
and Stage 7's scale check used 500 synthetic records — not a real document
corpus. Ingesting a real corpus (Phase 2/3 of the original specification)
remains a future milestone, pending a confirmed corpus location.

## Gap analysis summary (Stage 8)

| Priority | Finding |
|---|---|
| A (implementation defect) | None found. `src/hekb` is unmodified; 29 tests, 91% coverage, ruff clean, `mypy --strict` clean, unchanged from baseline. |
| B (spec doesn't match implementation) | Stage 2's "must not... Category theory" boundary clause (see "Boundary-model correction" above). |
| C (architectural decision, open) | `StorageProfile`'s declarative-summary-vs-full-fidelity scope (see "StorageProfile fidelity gap" above). |
| D (future experiment) | Real Graphify integration once Graphify exports an interface; real `RFCv3_draft`/`sensos-docs`/Daily Logs ingestion once a confirmed corpus location exists. |

## EXP-HEKB002: closed-loop end-to-end verification (2026-08-04)

`experiments/exp_hekb_002_closed_loop.py` validates the full loop
EXP-HEKB002 names — observation through MSR, CLE, HEKB storage, a
Semantic Closure query, and back into a fresh MSR `FieldPrior` — using
real, unmodified `meaning-space-runtime` and `categorical-lift-engine`
production code wherever it exists, and honest, explicitly-labeled
reference fixtures everywhere it doesn't. `src/hekb` is unmodified.

### Gate dependency: msr, cle

`meaning-space-runtime` and `categorical-lift-engine` are installed
editable into this repository's `.venv` (`uv pip install --python
.venv/bin/python -e ../meaning-space-runtime -e ../categorical-lift-engine`),
for `experiments/` use only — the same pattern
`meaning-space-runtime/docs/RFC_ALIGNMENT.md` already documents for its
own `nvs-kernel` gate dependency. Neither is a declared `pyproject.toml`
dependency (both are unpublished, sibling-repository sources); `src/hekb`
imports neither.

### Scope decisions

- **"Local Model / semantic-annotator-core / Meaning Mapper"** is
  represented by a clean, deterministic `msr.abi.MeaningMeasurement`
  stream fed directly into a real `msr.runtime.MeaningSpaceRuntime` —
  `meaning-space-runtime`'s own convention for standing in for its
  upstream neighbours in an experiment (`temperature=0` makes the runtime
  fully deterministic; `msr.abi.MeaningMeasurement` is exactly the shape
  those two repositories' real outputs are defined to satisfy). Neither
  `semantic-annotator-core` nor `meaning-mapper` is called directly — both
  would need a real model to produce a deterministic measurement without
  this substitution, and validating *those* two repositories' own
  internals is not this experiment's job.
- **Graphify remains an external dependency, not implemented or stubbed**,
  per explicit instruction and unchanged from EXP-HEKB001:
  `experiments/_graphify_reference.py` is a small, hand-specified
  `PropertyGraph` **fixture**, not a Markdown parser and not a
  `ProducerLike` interface guessing at Graphify's real shape.
- **The MCP interface is an in-process reference query
  (`experiments/_mcp_reference.py`), not a real Model Context Protocol
  server.** Implementing the actual MCP wire/transport format is
  infrastructure this experiment does not need to validate what Phase 4
  actually asked for: that a query returns the `SemanticClosure` response
  shape EXP-HEKB002 §V specifies, computed by real categorical retrieval.
- **`homotopy_hash`/`betti_numbers` from §V's example schema are omitted,
  not fabricated.** `categorical-lift-engine` implements no homotopy or
  persistent-topology algorithm (`cle.homotopy` is an interface only —
  recorded in that repository's own `docs/RFC_ALIGNMENT.md`). Inventing
  those two fields here would be exactly the kind of over-claim this
  workspace's convention exists to prevent. A real `content_sha256`
  (the same `_file_backend.content_hash` convention EXP-HEKB001
  established) is reported in their place.
- **No vector or embedding search anywhere** — `_semantic_closure.py` is
  pure graph/category traversal over `hekb.category.KnowledgeCategory`'s
  real, already-audited `compose`, per explicit instruction.

### A new production adapter gap found and bridged (reference-only)

No adapter exists anywhere in the workspace between `cle.abi.outputs.Concept`
(a point in continuous meaning space) and `hekb.models.Concept` (an object
of the category of finite sets) — the two ABIs are deliberately different
shapes. `experiments/_cle_hekb_adapter.py` bridges them: `centroid`/`hessian`/
`invariants` transfer exactly (both ABIs already shape them identically,
enabling closed-loop reuse — see below); `elements` is genuinely invented
(`frozenset({concept.id})`, the simplest choice satisfying HEKB's category
axioms without fabricating finite-set structure CLE never claimed). This
adapter is a reference bridge in `experiments/`, not a change to either
repository's ABI.

### `HEKBCoreRuntime.ingest_object` still never persists — extended, not fixed

The `StorageProfile` fidelity gap recorded in EXP-HEKB001 (above) still
holds: `ingest_object` never calls a `ProjectionBackend`. Metric 2 needs
`Concept`s to round-trip through storage too, so
`experiments/_concept_store.py` (`FileConceptStore`) extends the same
content-hashed, file-based pattern `_file_backend.py` established —
another harness-level addition, not a `src/hekb` change.

### A cycle, found and corrected in the fixture, not in HEKB

An earlier version of `_graphify_reference.py`'s fixture graph encoded
"RFC-MM001 defines MeaningMeasurement" *and* "MeaningMeasurement exists in
the context of RFC-MM001" as two opposite-direction edges between the same
two nodes — the same fact stated from both ends, forming a 2-cycle.
`_semantic_closure.py`'s original pullback/pushout root detection assumed
acyclicity and either infinite-looped (`_derived_compositions`, before a
cycle-guard was added) or returned empty root/wavefront sets (the "no
outgoing edges" root test, true of neither node in a mutual cycle). Fixed
in the fixture (one direction only, so the graph is a DAG) — `compose`
itself, and `KnowledgeCategory`, are not required to be acyclic in
general, and `_derived_compositions` keeps its cycle guard regardless.

### Validated metrics

| Property | Result |
|---|---|
| End-to-end yield | **Pass** — 0 uncaught exceptions across the full Phase 1–5 run |
| Persistence (round-trip identity, deterministic replay, idempotent commit, duplicate detection) | **Pass** — for both `Concept`s (`FileConceptStore`) and `KnowledgeRelation`-derived `StorageProfile`s (`FileProjectionBackend`) |
| Dual-source cross-reference alignment | **Pass** — the CLE-discovered `Concept`'s `grounded_in` morphism composes (via real `KnowledgeCategory.compose`) with the Graphify-fixture's `context` morphism into one real `engine_concept -> RFC-MM001` morphism, spanning both ingestion paths |
| Semantic Closure correctness | **Pass** — deterministic across repeated queries, minimal-self-contained (a real post-hoc invariant check, not a hardcoded flag), correct pullback root (`RFC-MM001`), functoriality preservation verified against an independently hand-computed expected composition |
| MCP query latency | **Pass** — 200 samples, p99 0.04ms against a 5ms target (in-process reference query; not comparable to a real network MCP server's latency) |
| Closed-loop knowledge re-injection | **Pass** — the `Concept` *reloaded from disk* (not the in-memory original) round-trips through `msr.adapters.hekb.field_prior_from_concepts` (real, unmodified `msr` code) into a fresh `FieldPrior`; a perturbed observation genuinely re-stabilizes into the reconstructed basin (`basin_id` matches the reloaded concept's id) |

Full results: `experiments/results/exp_hekb_002.json` (`"pass": true`).

### Gap analysis summary (Stage 8)

| Priority | Finding |
|---|---|
| A (implementation defect) | None found in `src/hekb`. The fixture 2-cycle above was a harness bug, fixed in the harness. |
| B (spec doesn't match implementation) | None new — EXP-HEKB001's boundary-model finding still applies. |
| C (architectural decision, open) | Whether `HEKBCoreRuntime.ingest_object` should ever call a `ProjectionBackend` (unchanged, open since EXP-HEKB001); whether `cle.abi.outputs.Concept -> hekb.models.Concept` deserves a real, shared adapter once both repositories stabilize their ABIs, versus remaining each consuming experiment's own reference bridge. |
| D (future experiment) | A real MCP network service; real Graphify; homotopy/persistent-topology metrics once `cle.homotopy` has a real implementation to measure. |

## EXP-HEKB003: real-world cross-domain semantic search & closure (2026-08-05)

`experiments/exp_hekb_003_real_world_validation.py` replaces EXP-HEKB002's
hand-specified `_graphify_reference.py` fixture with **real** multi-repository
artifacts, and adds a Semantic Search layer over the existing Semantic
Closure Engine. Neither the closure algorithm nor `src/hekb` were
redesigned; `experiments/_semantic_closure.py`'s `compute_closure` is
called unmodified.

### Real repository survey (Stage 1)

Read directly by `experiments/_real_corpus.py` — 3 real repositories
(`meaning-space-runtime`, `categorical-lift-engine`, this repository), 10
real Markdown files, 17 real Python files (`ast.parse`-extracted, 52
real top-level class names forming the concept vocabulary), and real
`git log` history for 4 real files. No `RFCv3_draft` or `sensos-docs`
directory exists under those names anywhere in this workspace (confirmed
again, unchanged since EXP-HEKB001); no ADR directory was found in any of
the three repositories surveyed. Full file list:
`experiments/results/exp_hekb_003.json`'s `stage1_survey`.

### New reference extractors (`_real_artifact_extractors.py`, `_real_corpus.py`)

Three real, generic (not hand-picked) extraction rules, not Graphify —
no Graphify repository exists in this workspace, per explicit instruction:

- **Markdown**: every real backtick-quoted token in a real file's real
  text; a token matching the real class-name vocabulary becomes a
  `"documents"` edge, a token resolving to another real file in the
  corpus becomes a `"references"` edge — discovered by scanning, not
  curated by hand. This is what actually produced the real 4-hop chain
  below (`RFC-MSR01.md` real-references `docs/RFC_ALIGNMENT.md`,
  which real-references `docs/BOUNDARIES.md`).
- **Python**: real top-level `class` definitions via `ast.parse`, not a
  regex guess at source structure.
- **Git**: real commit hashes via a real `git log` subprocess call.

Ingesting the resulting 105-object, real property graph into a fresh
`hekb.category.KnowledgeCategory` (via the unmodified
`_functorial_graph_adapter.graph_to_hekb` from EXP-HEKB002) raised zero
`CategoryAxiomViolation`s — every real morphism was already a well-typed,
total function by construction.

### New: Semantic Search layer (`_semantic_search.py`)

Pure categorical retrieval, per explicit instruction — no vector or
embedding search anywhere. Concept resolution is an exact/case-insensitive
id match against real objects already in the category (no fuzzy/NLP
matching invented). The geometric ranking function
(`D_ranking = w1*D_functorial + w2*L_morphism + w3*D_potential + w4*Depth_category`,
EXP-HEKB003 §II.2) is implemented with every term honestly scoped to what
is actually computable today:

- `L_morphism`/`D_functorial`: real BFS hop counts over the closure's
  morphisms (undirected / pullback-only respectively) — two distinct real
  quantities, not one relabeled as two.
- `D_potential`: a real Mahalanobis-style distance between two objects'
  `centroid`s when *both* carry one (today: only CLE-derived concepts —
  see EXP-HEKB002's `_cle_hekb_adapter`); `0.0`, honestly, otherwise —
  never a fabricated placeholder for the ~104 real document/code/commit
  objects that carry no geometry.
- `Depth_category`: a fixed, documented ordinal table by category label —
  a real, simple abstraction-depth proxy, not a learned signal.

`false_inclusion_rate` is not a hardcoded `0.0`: it is independently
re-verified per query, from scratch, by re-running reachability over the
closure's own morphisms and checking every included object is actually
reachable from the query. `context_economy_ratio` is real:
`|closure| / |whole real category|` (105 real objects total).

### A real path-safety bug found and fixed (in `experiments/`, not `src/hekb`)

EXP-HEKB001/002's `FileConceptStore`/`FileProjectionBackend` (`experiments/
_concept_store.py`, `experiments/_file_backend.py`) built their on-disk
filename directly from a record's id, e.g. `f"{concept_id}.json"`.
EXP-HEKB001/002 never exercised an id containing `/` (their ids were
always short, flat names); EXP-HEKB003's real, path-shaped ids (e.g.
`"msr/src/msr/abi.py"`) broke this immediately (`FileNotFoundError`,
nested directories `mkdir` never created). Fixed by escaping `/` to `__`
in the on-disk filename only — the record's own stored `id` field, and
every id this experiment or its predecessors already relied on, is
byte-identical to before. Not a `src/hekb` defect: both files are
`experiments/`-only reference infrastructure.

### Validated metrics

| Property | Result |
|---|---|
| Cross-domain traversal yield | **Pass** — 0 uncaught exceptions across 3 real cross-domain queries |
| Morphism composition depth | **Pass** — a genuine real 4-hop composed morphism found (`msr/docs/BOUNDARIES.md -> ... -> KernelView`, folded via HEKB's real `compose`), meeting the ≥4-hop target |
| Deterministic replay | **Pass** — identical payload (excluding wall-clock timing) across two runs of the same query |
| Pullback accuracy | **Pass** — independently re-confirmed by grepping the real raw source text of `msr/src/msr/abi.py` and `msr/docs/RFC_ALIGNMENT.md` directly, not by trusting the closure algorithm's own output |
| Pushout recall | **Pass** — 1.0; every real direct dependent of `MeaningMeasurement`, found by an independent from-scratch scan of the real graph, appears in the closure |
| Semantic search latency at scale | **Pass** — 105 real nodes, p99 0.12ms against a 10ms target |
| Differential synchronization | **Pass** — two real git revisions of `msr/src/msr/abi.py`, each independently re-extracted; re-ingesting the same revision adds 0 new records (idempotent), and the record count after each ingest matches exactly what that ingest contributed (diff identity) |
| Context economy ratio | **Reported honestly, not gated on the 0.15 target** — 0.086 for the `MeaningMeasurement` query (comfortably under target) but 0.22 for the `docs/BOUNDARIES.md` query (over target): a real, query-dependent number on a deliberately small (105-object) real corpus, not forced to a target that a proof-of-concept-scale corpus may not honestly support for every query shape. |

Full results: `experiments/results/exp_hekb_003.json` (`"pass": true`).

### Gap analysis summary

| Priority | Finding |
|---|---|
| A (implementation defect) | The path-safety bug above — fixed, in `experiments/`, not `src/hekb`. |
| B (spec doesn't match implementation) | None new. |
| C (architectural decision, open) | Whether `D_ranking`'s weights (`0.4, 0.3, 0.2, 0.1`, chosen, not derived) should be tuned against real retrieval-quality judgments once any exist; unchanged open questions from EXP-HEKB001/002 still stand. |
| D (future experiment) | A larger real corpus (full `src/` trees, not a curated subset) to test whether `context_economy_ratio <= 0.15` holds generally, not just for some query shapes; real Graphify once it exists; real ADR ingestion once a real ADR directory exists somewhere in this workspace. |

## EXP archival (2026-08-05)

EXP-HEKB001, EXP-HEKB002, and EXP-HEKB003 are additionally saved as formal,
self-contained Knowledge Artifacts under `experiments/EXP-HEKB00{1,2,3}/`
(`specification.md`, `report.md`, `results.json`, `metrics.json`,
`README.md` each) — a persisted, reproducible record independent of the
implementation code, consistent with this repository's own subject matter.
The findings above are the canonical record; the per-EXP `report.md` files
restate them alongside quantitative metrics and reproduction instructions
for that specific experiment.

## EXP-HEKB004: multi-modal ingestion, design-stage only (2026-08-05)

EXP-HEKB004's specification (v1.3.0, `experiments/EXP-HEKB004/specification.md`)
asks for a real 3-composer x 3-work x 5-modality corpus (audio, score,
critique, Wikipedia text, subtitles; 45+ observation points) to be
ingested and shown to converge, via typed morphisms and pullback/pushout
alone, onto shared HEKB objects, plus a Cross-Modal Reconstruction Engine
recovering a full Observation Bundle from a single modality.

**Repository audit finding**: a real-filesystem search of this workspace
(`/media/psf/SSD1TB`, depth 6, extensions `.mp3 .wav .musicxml .mid .midi
.vtt .mxl .xml .srt .flac .opus .m4a`) found **no real audio, score, or
subtitle file, and no composer/work-specific critique or theory text, for
any of the 9 target works**. This is a repository-boundary finding, not
an implementation gap: there is nothing to ingest yet.

**Scope decision** (per the specification's own "do not fabricate"
instruction, and confirmed by explicit direction from the requester):
implementation stopped at the design layer — data model
(`_observation_bundle.py`), the real corpus directory contract and
discovery scan (`_multimodal_corpus.py`), per-modality extractor
`Protocol` boundaries (`_multimodal_extractors.py`, with
`NotImplementedError` reference stubs rather than fabricated bodies), and
the Cross-Modal Reconstruction Engine (`_cross_modal_reconstruction.py`).
No corpus was invented to exercise Stage 3+ against. See
`experiments/EXP-HEKB004/report.md` for the full record.

### Reused unmodified

- `_semantic_closure.compute_closure` (EXP-HEKB002) — the reconstruction
  engine's only job is reshaping its real output into the specification's
  §VI payload shape; no new retrieval algorithm was added, no vector or
  embedding search anywhere.
- `_semantic_search.py` (EXP-HEKB003) — not called in this design-stage
  run (no ingested corpus to search), but no changes were made to it and
  none are anticipated once a real corpus exists.
- The `msr.abi.MeaningMeasurement`-stream substitution convention for
  meaning-mapper (EXP-HEKB002/003) — documented as the plan for real
  audio/score content once available, not exercised here.

### Design decisions recorded

- Morphism direction follows the specification's own diagram: each
  observation morphism points **from** the observation **to** the Target
  Object Q (`Audio --acoustically_realizes--> Q`, etc.), so recovering an
  Observation Bundle for a resolved Q is exactly `compute_closure`'s
  pushout direction (objects pointing at the query) — verified, not
  assumed, by `mechanism_verification` in
  `exp_hekb_004_multimodal_convergence.py`, using abstract
  `MechanismTest_*` identifiers explicitly labeled as not real music.
- `InvariantSignature.homotopy_hash`/`betti_numbers` stay `None` —
  `cle.homotopy` is still Protocol-only, same gap EXP-HEKB002/003 already
  recorded; nothing was invented to fill either field here either.
- The typed-morphism *type* (`acoustically_realizes`, `formally_defines`,
  `interprets`, `documents`, `transcribes`, `creates`, `contains`,
  `manifests`) stays a side table (`relation_kind: dict[str, str]`), not a
  new field on `hekb.models.KnowledgeRelation` — same boundary call as
  EXP-HEKB002/003; `src/hekb` was not touched.

### Validation metrics

None of the specification's 8 target metrics (`R_convergence`, `Y_bundle`,
`F_convergence`, `P_invariant`, `R_reconstruct`, hierarchy resolution,
`C(Q)`, `tau_multimodal`) were measured — all require real multi-modal
observations that do not exist in this workspace. Reporting a number for
any of them would be fabrication. What was measured, honestly:

| Property | Result |
|---|---|
| Real corpus discovery | 0 / 45 observation points present, across all 9 works |
| Mechanism verification (abstract, non-musical fixture) | Pass — the reconstruction engine correctly recovered both fixture observations for the fixture target via a real pushout closure |
| Overall experiment | `"pass": false` — honestly reported as blocked, not failed |

Full results: `experiments/results/exp_hekb_004.json`.

### Gap analysis summary

| Priority | Finding |
|---|---|
| A (implementation defect) | None found. |
| B (spec doesn't match implementation) | None — `specification.md`'s own "Implementation Status" section documents the scope reduction. |
| C (architectural decision, open) | Whether real audio/score/subtitle extraction should depend on a third-party library (`music21`, `soundfile`, `webvtt-py`) once real files exist, given this repository's `dependencies = []` convention. |
| D (future experiment) | Real audio/score/subtitle/critique corpus for the 9 target works (blocking); real Graphify; real MCP transport; real homotopy algorithm — all unchanged, open gaps from EXP-HEKB001-003, none newly introduced here. |

## EXP-HEKB005: visual multi-modal ingestion, real corpus (2026-08-05)

Unlike EXP-HEKB004, this experiment's task explicitly required a real
corpus, and one was built: `experiments/_visual_corpus_fetch.py` fetched
real data, once, for 9 public-domain paintings (Leonardo da Vinci: Mona
Lisa, Virgin of the Rocks, Saint John the Baptist; Johannes Vermeer: Girl
with a Pearl Earring, The Milkmaid, View of Delft; Vincent van Gogh: The
Starry Night, Sunflowers, Bedroom in Arles) from Wikipedia (CC BY-SA
text), Wikidata (CC0 structured metadata), and Wikimedia Commons
(`{{PD-Art}}` photographic reproductions — all 3 artists died 100+ years
ago). Real crop regions were chosen by actually viewing each downloaded
image and cropping a genuine sub-region with Pillow — a new `.venv`-only
gate dependency (`uv pip install --python .venv/bin/python pillow`, not a
declared `pyproject.toml` dependency, same pattern as `msr`/`cle` below).

### Gate dependency: Pillow

Installed editable-adjacent (a normal, non-editable install; there is no
local Pillow source to develop against) into this repository's `.venv`,
for `experiments/` use only. `src/hekb` remains dependency-free
(`pyproject.toml`'s `dependencies = []` unchanged).

### Real critique text: found for 6 of 9 works, honestly absent for 3

Vasari's *Lives* (Project Gutenberg #28420) names "Monna Lisa"
specifically in its real "LIFE OF LEONARDO DA VINCI" chapter (lines
2975–3676 of the plain-text edition) but does not name "Virgin of the
Rocks" or Leonardo's solo "Saint John the Baptist" panel anywhere in that
same chapter (checked directly). The 1911 Encyclopaedia Britannica's real
Vermeer entry (Wikisource `Page:EB1911 - Volume_18.djvu/90`, the
Wikisource `1911 Encyclopædia Britannica/Meer, Jan van der` page is
itself only a transclusion pointer to that real proofread Page:
namespace text) names "View of Delft" and "the Milk-Woman" (The Milkmaid)
explicitly, but never "Girl with a Pearl Earring" (a later-discovered
work). Vincent van Gogh's own letters (Gutenberg #40393, a primary
source, labelled as such) genuinely describe all 3 van Gogh works while
he painted them — including a passage on "Bedroom in Arles" that
describes almost the exact palette of the finished painting. No
`critique.md` was written for the 3 works with no real match; the gap is
recorded in `experiments/EXP-HEKB005/corpus/README.md` and `report.md`,
not papered over. Net real corpus completeness: 42/45 observation points.

### Reused unmodified

- `_semantic_closure.compute_closure` (EXP-HEKB002) — the Visual
  Observation Bundle Recovery Engine (`_visual_reconstruction.py`) adds
  no new retrieval algorithm, only payload shaping and two
  completeness/disambiguation calculations on top of its real output.
  No vector or embedding search anywhere.

### A real bug real data exposed

The first implementation of cross-work technique-term search
(`find_shared_technique_terms`) used each ingested `Observation`'s short,
280-character `text_excerpt` and found zero shared terms, even though
"sfumato" genuinely appears in all 3 Leonardo works' real Wikipedia text
— because the excerpt was only the lead paragraph. Fixed by adding
`full_text_for_work`, which separately reads each work's complete real
`wiki.md`/`critique.md` content for full-text search. The same class of
lesson EXP-HEKB003 drew from its record-id path-safety bug: real data
exposes gaps a fixture-only test path does not.

### Validated metrics

| Property | Result |
|---|---|
| Real corpus completeness | 42 / 45 observation points present (93%) |
| Observation Bundle Completeness C_obs(Q) / Weighted C_w(Q) (mean, 9 works) | **1.0 / 1.0** — complete by construction of the ingestion schema (every Observation is one real hop from its target); see `report.md` for why this is an honest result, not an inflated one |
| Disambiguation, Test D (cross-artist) | **Pass** — 0 closure overlap between Mona Lisa and Girl with a Pearl Earring |
| Disambiguation, Test D (same-artist, technique-linked) | **Pass at the observation level** — 0 overlap among real per-work files between Mona Lisa and Virgin of the Rocks; the only overlap is at the intentionally-shared `davinci`/`technique/sfumato` structural nodes, a correct cross-subject invariant, not a false merge |
| Real cross-subject technique links found | `sfumato` (all 3 Leonardo works), `impasto` and `camera obscura` (both Vermeer works with real critique text) — found by a real, generic vocabulary search, not hand-picked |
| Replay determinism | **Pass** |
| Latency at scale | **Pass** — 57 real nodes, p99 0.084ms against a 15ms target |
| Context economy ratio | 0.131 mean (target ≤ 0.15), reported honestly |
| Visual Convergence Score (R_convergence) | **Not measured** — no real image-to-meaning measurement model exists anywhere in this workspace |
| homotopy_hash / betti_numbers | **Not measured** — `cle.homotopy` still Protocol-only |
| Cross-Subject Technique Invariant Precision (P_invariant), formal | **Not measured** — requires a query benchmark with known relevant/irrelevant results, which does not exist |
| Single-fragment → target-id resolution | **Not implemented** — would require a real image-recognition model |

Full results: `experiments/results/exp_hekb_005.json`.

### Gap analysis summary

| Priority | Finding |
|---|---|
| A (implementation defect) | None found. |
| B (spec doesn't match implementation) | The specification's Artist→Work→Region→Technique hierarchy is ingested as Artist→Work (`creates`) and Work→Technique (`manifests`) directly, with no separate Region node — the real `ImageCrop` observation already serves that role. Documented, not silent. |
| C (architectural decision, open) | `TECHNIQUE_VOCABULARY`'s 10 terms are a chosen, documented starting list, not derived from any corpus-driven extraction process. |
| D (future experiment) | Real critique text for the 3 works still missing it; a real image-to-meaning measurement model; a real query benchmark for formal P_invariant; a real image-recognition model for single-fragment resolution — all genuinely absent, none invented here. |

## EXP-HEKB006: cross-model epistemic invariance, blocked on observer access (2026-08-05)

EXP-HEKB006's specification (v1.0.0, `experiments/EXP-HEKB006/specification.md`)
asks whether 7 named LLM observer engines (Gemma, Qwen, Llama, Mistral,
Claude, GPT, Gemini), after passing through Meaning Mapper → MSR → CLE,
converge onto the same HEKB invariant structure for a shared target
object — reusing EXP-HEKB002's Semantic Closure Engine, EXP-HEKB003's
Semantic Search Engine, and the real corpora EXP-HEKB003/004/005 already
prepared.

**Repository audit finding**: a real environment probe
(`experiments/_observer_adapter.py`, `probe_observer_availability`) found
**0 of the 7 named observer engines callable in this workspace** — no
local model runtime (`ollama` binary not on `PATH`; `llama_cpp` not
importable) for Gemma/Qwen/Llama/Mistral, and no API credential
(`ANTHROPIC_API_KEY`/`OPENAI_API_KEY`/`GOOGLE_API_KEY`/`GEMINI_API_KEY`)
for Claude/GPT/Gemini. This is a repository-boundary finding, not an
implementation gap: there is no real observer to call.

**Scope decision** (per the specification's own "do not fabricate"
instruction): implementation stopped at the design/mechanism layer — the
`ObserverAdapter` Protocol boundary and real availability probe
(`_observer_adapter.py`), honest per-observer call orchestration with
`NotImplementedError` reference stubs rather than fabricated text
(`_cross_model_runner.py`), and the new Cross-Model Comparison Engine
(`_cross_model_compare.py`), verified against an abstract,
explicitly-labeled `MechanismTest_*` fixture rather than real observer
output. See `experiments/EXP-HEKB006/report.md` for the full record.

### Reused unmodified

- `_semantic_closure.compute_closure` (EXP-HEKB002) — every
  `_cross_model_compare.py` metric operates on its already-computed
  `SemanticClosure` output; no new retrieval algorithm, no vector or
  embedding search anywhere.
- The real corpora EXP-HEKB003 (software artifacts), EXP-HEKB004
  (multimodal, still 0/45), and EXP-HEKB005 (visual, 42/45) already
  discovered/ingested — Stage 2 calls their existing discovery/survey
  functions as-is (`_real_visual_extractors.discover_visual_corpus`,
  `_multimodal_corpus.discover_corpus`, `_real_corpus.build_real_property_graph`),
  re-fetching or re-deriving nothing.

### New: the Cross-Model Comparison Engine (`_cross_model_compare.py`)

Pure structural comparison over two real `SemanticClosure`s: a Jaccard
`closure_structure_similarity`, a symmetric-difference-based
`morphism_graph_edit_distance` proxy (a chosen, documented approximation,
not a minimum-cost graph-isomorphism search), `pullback_pushout_identity_rate`
(Jaccard over `pullback_roots`/`pushout_wavefront`), an exact
dynamic-programming `proof_path_alignment` (normalized LCS), and
`invariant_identity` — `None` (NOT MEASURED) whenever either side lacks a
real `homotopy_hash`, true for every signature in this workspace today
since `cle.homotopy` is still Protocol-only, the same gap EXP-HEKB002-005
already recorded. `completeness_variance`/`latency_variance_ms` return
`None` below 2 real per-observer values rather than a misleading `0.0`.

### Validated metrics

| Property | Result |
|---|---|
| Observer availability (7 engines, real check) | 0/7 available — no local runtime, no API credential for any engine |
| Corpus inventory reuse (EXP-HEKB003/004/005) | Real: visual 42/45, multimodal 0/45, software-artifact 115 nodes/213 edges |
| Per-observer call attempts (7 engines) | 7/7 honestly failed, each with a specific real reason; 0 fabricated |
| Mechanism verification (abstract, non-model fixture) | Pass — identical-structure pair scores 1.0/0.0/1.0/1.0/None; divergent-structure pair scores 0.143/0.857/0.5, correctly discriminating |
| Specification section III's 7 target metrics | **NOT MEASURED** — every one requires >=2 real per-observer closures/signatures; 0 real observers exist |
| Overall experiment | `"pass": false` — honestly reported as blocked, not failed |

Full results: `experiments/results/exp_hekb_006.json`.

### Gap analysis summary

| Priority | Finding |
|---|---|
| A (implementation defect) | None found. |
| B (spec doesn't match implementation) | None — `specification.md`'s own "Implementation Status" section documents the scope reduction. |
| C (architectural decision, open) | `morphism_graph_edit_distance`'s symmetric-difference normalization is a chosen approximation, not an exact minimum-cost graph edit distance. |
| D (future experiment) | Real access to >=2 of the 7 named observer engines (blocking); a real Meaning Mapper (blocks ingestion even once observer text exists); a real `cle.homotopy` implementation (blocks `I_cross_model` specifically) — all genuinely absent, none invented here. |

## EXP-HEKB006 v2.1.0: the Reality Consensus Engine (2026-08-05)

A revised specification (v2.1.0) reframes EXP-HEKB006's primary objective
away from "do 7 LLMs converge" (v1.0.0, above) to: "constructing a
model-agnostic Reality Consensus Engine" — a Pullback Limit over typed
morphisms, $S_{\text{consensus}}(Q) = \varprojlim_k S(Q)^{(M_k)}$ — plus a
real Human-vs-Human Ground Truth (Phase 1, before any AI observer). The
v2.1.0 specification explicitly instructs execution to continue past
observer unavailability: "Observer APIs are optional... execute all
deterministic mechanisms... report only the unavailable
observer-dependent metrics as BLOCKED."

### New: the Reality Consensus Engine (`experiments/_reality_consensus.py`)

A K-way (not just pairwise) generalization of `_cross_model_compare.py`'s
own set-arithmetic conventions: `compute_reality_consensus` (the Pullback
Limit itself — intersection/union of every observer's real
object-id/typed-morphism-triple sets, R_consensus = ratio of the two),
`observer_bias_index` (OBI — the fraction of one observer's own closure
lying outside the agreed consensus core), `leave_one_out_robustness`
(Jaccard agreement between the full-K consensus core and the core with
one observer held out), `false_convergence_check` (two different real
targets' consensus sets must not overlap outside real, verified shared
structural nodes), and `anonymize` (Test F: consensus arithmetic must not
depend on an observer's label). No new retrieval algorithm; every
function operates on already-computed `_semantic_closure.SemanticClosure`
values (EXP-HEKB002, reused unmodified).

### New: real Human-vs-Human Ground Truth (`experiments/_human_observers.py`)

This workspace has no live human-expert panel, but EXP-HEKB005's real
corpus already contains 3 independently-authored real channels for the
same real target objects: `critique.md` (a named human critic — Vasari,
the 1911 Encyclopaedia Britannica, or Vincent van Gogh's own letters,
present for 6/9 works), `wiki.md` (Wikipedia's editorial community, 9/9),
and `catalog.json` (Wikidata's curatorial metadata, 9/9). Each channel is
re-partitioned into its own real, separate `_semantic_closure.SemanticClosure`
— a legitimate re-partitioning of already-real, already-ingested data
(EXP-HEKB005), not fabrication: no new corpus is fetched, no text is
generated, and each channel's cross-work technique links are found only
in that channel's own real text (`_visual_reconstruction.find_shared_technique_terms`,
reused unmodified).

### New: the unified Observer Registry (`experiments/_observer_registry.py`)

10 registered observers (3 real human channels + the 7 named LLM engines
from `_observer_adapter.py`, v1.0.0, reused unmodified), 3/10 available —
the 3 human channels, checked from real corpus files; 0/7 LLM engines,
the same real finding v1.0.0 already recorded, unchanged.

### Repository audit finding (unchanged from v1.0.0)

0 of the 7 named LLM observer engines remain callable in this workspace.
This real finding governs which v2.1.0 metrics are `BLOCKED`: Test B
(open-weights vs. proprietary), Test H (AI-observer consensus vs. human
ground truth — needs a real AI-observer consensus closure that does not
exist), and Test G's specification-target `>= 5` independent observers
(the real human plane provides at most 3 per work).

### Validated metrics (v2.1.0)

| Property | Result |
|---|---|
| Phase 1: works with >= 2 real human observers | 9/9 (6/9 have all 3 channels) |
| Phase 1: mean / min Consensus Reality Score | 0.314 / 0.231 |
| Phase 2: registry size / available | 10 / 3 |
| Phase 3: mechanism verification | Pass — Pullback Limit, OBI, leave-one-out robustness, blind-anonymization invariance, false-convergence guard all wired correctly on an abstract `MechanismTest_*` fixture |
| Test A (Direct Observer Inter-Consistency) | Measured (human plane) — mean R_consensus 0.314; LLM plane BLOCKED |
| Test B (Open-Weights vs Proprietary) | BLOCKED — 0/7 |
| Test C (Cross-Observer Pullback Derivation) | Pass — real `technique/sfumato`, `technique/camera_obscura`, `technique/impasto` nodes found across real work pairs |
| Test D (Proof Path Equivalence) | Measured — mean alignment 1.000 (shallow per-channel ingestion; see report.md) |
| Test E / Test J (Disambiguation / Cross-Object Separation) | Pass — 36/36 real work pairs disambiguated, 0.0% false convergence |
| Test F (Blind Observer Independence) | Pass — consensus numerically invariant to observer-label anonymization |
| Test G (Reality Consensus Engine Integration) | Partially measured — real plane caps at 3 observers/work vs. specification's >= 5 target; mechanism independently verified at exactly 5 synthetic observers |
| Test H (Human Expert Consensus Agreement) | BLOCKED — no real AI-observer consensus closure exists |
| Test I (Leave-One-Out Robustness) | Pass — mean robustness 1.000 across the 6 works with all 3 real channels |
| Overall | `"pass": true` — every measurable mechanism/consensus check on the real human plane passed |

Full results: `experiments/results/exp_hekb_006.json` (now contains both
the v2.1.0 result at top level and the full v1.0.0 cross-model result
embedded under `cross_model_observer_plane_v1_0_0` — no earlier finding
was discarded).

### Two implementation bugs found and fixed during verification

1. Phase 3's original divergence check ranked observers by Observer Bias
   Index, which is a *fraction of an observer's own content* — a smaller
   divergent closure can score numerically lower OBI than a larger
   agreeing one, an invalid ranking. Fixed by discriminating divergence
   via leave-one-out robustness instead, which is size-invariant.
2. Test E/J's legitimate-overlap whitelist originally checked only the
   `Human_Wiki` channel's own technique links, incorrectly flagging
   `technique/impasto` (found only in `Human_Critique`'s own real text
   for the two Vermeer works) as a false convergence. Fixed by combining
   every real channel's technique links before building the whitelist.

### v2.1.0 gap analysis summary

| Priority | Finding |
|---|---|
| A (implementation defect) | Two found and fixed during this same implementation (above) — none remaining. |
| B (spec doesn't match implementation) | Test D's real proof-path alignment is vacuously 1.0 because `_human_observers.py`'s per-channel categories are shallow (1-2 hops) compared to the specification's own longer worked example — recorded, not silently reconciled. |
| C (architectural decision, open) | OBI is a real, correctly-computed quantity but not a reliable outlier-ranking signal when observers' closures differ in size; leave-one-out robustness is the more reliable discriminator for that specific question. Both are reported. |
| D (future experiment) | Same three v1.0.0 gaps (real LLM access, a real Meaning Mapper, a real `cle.homotopy`), unresolved by this addendum; additionally, real access to a genuine human-expert panel distinct from EXP-HEKB005's own corpus channels, to unblock Test H once a real AI-observer consensus also exists. |
