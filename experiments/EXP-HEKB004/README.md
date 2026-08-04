# EXP-HEKB004: Multi-Modal Target Ingestion, Invariant Convergence & Cross-Subject Retrieval Validation

## Status

**Design-stage, implementation paused.** Not a completed, validated
experiment like EXP-HEKB001-003 — see `report.md` for why.

## Purpose

Demonstrate that heterogeneous observations (audio, score, critique,
Wikipedia text, subtitles) of the same real musical work converge,
through typed morphisms and pullback/pushout algebra alone (no vector or
embedding search), onto the same HEKB object — and that a single
modality's observation can recover the full Observation Bundle for that
object (Cross-Modal Reconstruction).

## Target Repository

`/media/psf/SSD1TB/HEKBv2`.

## Target Specification

EXP-HEKB004 v1.3.0 (full text in `specification.md`).

## Why this is paused

A real-filesystem search of this workspace found no real audio
(`.mp3`/`.wav`), score (`.musicxml`/`.mid`), or subtitle (`.vtt`) file,
and no composer/work-specific critique or theory text, for any of the 9
target works. Per the specification's own "do not fabricate" instruction
and explicit direction from the requester, this experiment stops at
designing the interfaces and boundaries a real corpus would flow through,
rather than inventing data to demonstrate them against.

## What exists today

- `experiments/_observation_bundle.py` — Observation Bundle data model,
  typed-morphism vocabulary, Target Object hierarchy.
- `experiments/_multimodal_corpus.py` — the 9-work catalog and the real
  corpus directory contract + discovery scan (`experiments/EXP-HEKB004/corpus/`,
  currently empty — see its `README.md`).
- `experiments/_multimodal_extractors.py` — per-modality extractor
  `Protocol`s (the contract, not a concrete implementation).
- `experiments/_cross_modal_reconstruction.py` — the Cross-Modal
  Reconstruction Engine, reusing EXP-HEKB002's `_semantic_closure.compute_closure`
  unmodified.
- `experiments/exp_hekb_004_multimodal_convergence.py` — orchestrator:
  runs Stage 1 (real corpus discovery, honestly reports 0/45 present) and
  a `mechanism_verification` self-check (abstract, non-musical
  `MechanismTest_*` identifiers, proving the reconstruction engine's
  wiring is correct) — Phases 1-3 are reported as `blocked_on_real_corpus`.

## Reproduction

```bash
cd /media/psf/SSD1TB/HEKBv2
source .venv/bin/activate
cd experiments
python exp_hekb_004_multimodal_convergence.py
```

Results land in `experiments/results/exp_hekb_004.json`
(`"pass": false` — blocked, not a failure of the mechanism itself; see
`report.md`).

## Quality Gates

```bash
cd /media/psf/SSD1TB/HEKBv2
source .venv/bin/activate
python -m pytest -q
ruff check .
ruff format --check .
python -m mypy .
```

See `report.md` for measured results.

## Next steps

Supply real files under `experiments/EXP-HEKB004/corpus/` per its
`README.md`'s contract, then re-run
`exp_hekb_004_multimodal_convergence.py` — no change to the mechanism is
anticipated, only implementing the `NotImplementedError` reference stubs
in `_multimodal_extractors.py` against real files.
