# EXP-HEKB001 — Report

## Implementation Summary

EXP-HEKB001 validated HEKB's persistence boundary against a real, file-based
`ProjectionBackend` instead of the test-only `InMemoryProjectionBackend`
`src/hekb` ships. No production code was modified; every new component was
added under `experiments/`:

- `experiments/_file_backend.py` — `FileProjectionBackend`, a real,
  deterministic, SHA-256-content-hashed JSON file store implementing
  `hekb.storage.ProjectionBackend`. Lives outside `src/hekb`, depends on
  `hekb`, never the reverse.
- `experiments/_lineage_fixture.py` — the RFC-MM001/RFC-MSR01
  defines/consumes/provenance example from the specification itself, built
  as real `hekb.models.Concept`/`KnowledgeRelation` values.
- `experiments/exp_hekb_001_persistence_validation.py` — the orchestrator:
  Stage 4 (persistence), Stage 5 (cross-reference lineage, synthetic
  fixture), Stage 6 (storage validation against the real mounted path this
  repository lives at), and a synthetic-only Stage 7 (scale/lookup
  latency).

Graphify integration (Stage 3) was **not** implemented or stubbed: no
Graphify repository exists anywhere in the workspace, and the
specification's own instruction ("do not reimplement Graphify, only
validate the interface") had no real interface to validate against.
Recorded as an external dependency in `docs/RFC_ALIGNMENT.md`.

## Architectural Findings

- **Category theory is HEKB's core, not a leaked responsibility.** The
  specification's Stage 2 boundary model ("HEKB must NOT become
  responsible for... Category theory") does not describe this repository:
  `hekb.category` (category axioms, the Homotopic Update Law, pushouts,
  pullbacks, the tensor/internal-hom adjunction) is HEKB's entire
  algebraic core, by its own explicit self-description. Recorded as a
  spec/implementation boundary-model mismatch, not a defect — no code
  changed as a result.
- **`StorageProfile` fidelity gap.** `hekb.storage.to_storage_profile`
  emits a *declarative* summary of a morphism (id, domain, codomain,
  invariants) — it does not include the morphism's `mapping`, and
  `HEKBCoreRuntime.ingest_object` never calls the backend at all, so no
  `Concept` ever reaches a `ProjectionBackend` in the shipped design. Round-
  trip identity was validated for exactly what the ABI actually persists
  (the `StorageProfile`), not a stronger, unsupported claim about full
  object reconstruction. Left open as a Priority C architectural question,
  not decided unilaterally.

## Boundary Findings

- `src/hekb` was not modified in any way.
- `tests/test_storage_ignorance_audit.py`'s AST scan (forbidding database
  driver imports under `src/hekb`) remained satisfied throughout —
  `FileProjectionBackend` lives in `experiments/`, outside its scope, and
  uses only `json`/`hashlib`/`pathlib` regardless.
- No responsibility leaked into HEKB during this work: HEKB never touched
  measurement, trajectory generation, or Graphify-style parsing.

## Validation Metrics

| Property | Result |
|---|---|
| Round-trip identity | Pass — 4/4 `StorageProfile` records, `Hash(Load(Save(O))) == Hash(O)` |
| Deterministic replay | Pass — a fresh `FileProjectionBackend` instance reproduces an identical record set |
| Idempotent commit | Pass — 0 duplicate records on redundant write |
| Duplicate detection | Pass — `CategoryAxiomViolation` raised before the backend is ever touched |
| Immutability | Pass — `Concept`, `KnowledgeRelation`, `StorageProfile`, `EpistemicGraphSnapshot` all reject mutation |
| Recovery | Pass, scoped to what `StorageProfile` carries |
| Cross-reference lineage | Pass — real composed morphism via `KnowledgeCategory.compose` |
| Lookup latency (synthetic, 500 records) | Pass — p95 0.77ms against a 5ms target |

Full measured values: `results.json` (copied verbatim from
`experiments/results/exp_hekb_001.json` as committed at `4379eb9`).

## Quality Gates

pytest: 29 passed · coverage: 91% (`src/hekb`, unchanged from pre-experiment
baseline; no `fail_under` gate configured) · ruff check: clean · ruff
format --check: clean · mypy --strict (`mypy .`): clean.

## Lessons Learned

1. **A commissioned specification's premises must be checked against the
   actual repository before implementation begins.** EXP-HEKB001 assumed a
   real persistence layer and a real Graphify producer; neither existed.
   Auditing first (Stage 1) turned two potential dead-ends into an honest,
   scoped deliverable instead of a failed or fabricated one.
2. **"Storage ignorance" is narrower than "never touches a filesystem."**
   The static audit test only forbids database-*driver* imports, not file
   I/O — this is what made a real, deterministic file-based backend
   possible without violating HEKB's own architectural boundary or
   requiring a Priority-A code change.
3. **Round-trip identity claims must be scoped to what the ABI actually
   carries.** Validating against a stronger, unstated claim (full object
   reconstruction) would have been dishonest; the fidelity gap is real and
   was recorded, not hidden or silently "fixed" by widening `StorageProfile`
   without authorization.
