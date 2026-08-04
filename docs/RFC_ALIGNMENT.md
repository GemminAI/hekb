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
