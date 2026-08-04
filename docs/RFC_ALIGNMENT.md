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
