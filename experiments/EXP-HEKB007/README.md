# EXP-HEKB007: End-to-End Epistemic Pipeline & Observation Bundle Round-Trip System Integration Validation

## Status (v1.1.0, current)

**Measured and passing on every mechanism this workspace can honestly
execute.** Per the specification's own governing instruction ("do not stop
merely because proprietary APIs, remote services, or external observers are
unavailable... implement every executable mechanism first, report BLOCKED
only for the unavailable portion"), this experiment integrates two
previously-separate real pipelines into one shared
`hekb.category.KnowledgeCategory` for the first time — EXP-HEKB002/003's
real MSR->CLE crystallization and EXP-HEKB005's real 9-work visual corpus —
and adds a genuinely new component, a real standalone TCP HEKB MCP Daemon,
since every prior MCP interface in this workspace was deliberately
in-process only. See `report.md` for full findings and `results.json` for
every number.

## Purpose

Validate the complete pipeline `Raw Observation -> Meaning Mapper -> MSR ->
CLE -> HEKB -> Semantic Closure -> HEKB MCP -> Observation Bundle Recovery`
as one integrated loop, reusing every already-real component from
EXP-HEKB001-006 unmodified, building only the missing orchestration glue.

## Target Repository

`/media/psf/SSD1TB/HEKBv2`.

## Target Specification

EXP-HEKB007 v1.1.0 (full text in `specification.md`).

## What already existed, reused unmodified

- `src/hekb` — the category-theoretic HEKB core (`KnowledgeCategory`,
  pushout/pullback, the Homotopic Update Law).
- `experiments/_semantic_closure.py` — the Semantic Closure Engine.
- `experiments/_semantic_search.py` — categorical retrieval/ranking.
- `experiments/_msr_cle_pipeline.py` — real MSR settling into a real CLE
  crystallization (`msr`/`cle` gate-installed, per `docs/RFC_ALIGNMENT.md`).
- `experiments/_cle_hekb_adapter.py` — CLE `Concept` -> HEKB `Concept`.
- `experiments/exp_hekb_005_visual_reconstruction.ingest_real_corpus` and
  `experiments/_visual_reconstruction.py` — the real 9-work visual corpus
  (3 da Vinci, 3 Vermeer, 3 van Gogh) and its Observation Bundle recovery
  (`C_obs(Q)`/`C_w(Q)`, disambiguation), already validated by EXP-HEKB005.
- `experiments/_mcp_reference.py` — the in-process MCP query interface this
  experiment's new daemon wraps, not replaces.

## What is genuinely new here

- `experiments/_mcp_daemon.py` — a real, standalone stdlib-only TCP daemon
  (`socketserver.ThreadingTCPServer`) wrapping `_mcp_reference.MCPReferenceQuery`
  unmodified, plus a real concurrent-client load-test harness.
- `experiments/exp_hekb_007_epistemic_pipeline.py` — the orchestrator:
  - Stage 1: reuse EXP-HEKB005's real corpus ingestion, unmodified.
  - Stage 2: reuse EXP-HEKB002/003's real MSR->CLE upstream, unmodified.
  - Stage 3: **the missing integration glue** — bridge the MSR/CLE
    crystallized `Concept` into the same category the real corpus already
    occupies, with a true provenance edge (never a fabricated link to any
    specific painting).
  - Stage 4: Semantic Closure + Observation Bundle recovery for the real
    corpus query, a small closure for the engine concept, and a
    disambiguation check proving the two do not false-converge.
  - Stage 5: Test D — the new real TCP daemon under 100 real concurrent
    clients.
  - Stage 6: full-loop replay determinism (two cold-start runs compared
    bit-for-bit, wall-clock daemon timing excluded, as every prior
    experiment's own replay check already does).
  - Stage 7: fault injection — real category-axiom violations, an
    unstabilized-trajectory CLE call, and malformed daemon requests, all
    asserted to be quarantined rather than crashing.

## Reproduction

```bash
cd /media/psf/SSD1TB/HEKBv2
source .venv/bin/activate
cd experiments
python exp_hekb_007_epistemic_pipeline.py   # writes results/exp_hekb_007.json
```

Results land in `experiments/results/exp_hekb_007.json` (`"pass": true`).
Network latency (Stage 5) is real wall-clock and will vary slightly between
runs; every other stage is bit-identical across runs (Stage 6 verifies this
directly).

## Quality Gates

```bash
cd /media/psf/SSD1TB/HEKBv2
source .venv/bin/activate
python -m pytest -q
ruff check .
ruff format --check .
python -m mypy --strict experiments/exp_hekb_007_epistemic_pipeline.py experiments/_mcp_daemon.py --explicit-package-bases --ignore-missing-imports
```

`python -m mypy` alone only checks `src/hekb` (this repository's
`pyproject.toml` scopes `packages = ["hekb"]`); the explicit invocation
above is how every `experiments/` module, old and new, is actually held to
the same strict bar. See `report.md`'s Quality Gates section for exact
current counts.

## Next steps

A real Meaning Mapper (would let Stage 2 start from actual audio/image
bytes instead of a synthetic settle stream), a real `cle.homotopy`
implementation (would unblock `R_compress` and `invariant_signature`), a
real single-fragment resolution model (would unblock `RRF`/`Y_roundtrip`),
and a persistent, multi-session HEKB store (would unblock the Knowledge
Health Vector growth rate) are all recorded as open architectural gaps in
`report.md`, not attempted here.
