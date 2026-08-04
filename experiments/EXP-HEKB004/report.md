# EXP-HEKB004 — Report (Interim / Design-Stage)

## Implementation Summary

EXP-HEKB004 was commissioned to validate multi-modal invariant convergence
and Observation Bundle reconstruction across a real 3-composer x 3-work x
5-modality corpus (45+ observation points), reusing EXP-HEKB002's
Semantic Closure Engine and EXP-HEKB003's Semantic Search Engine
unmodified — no vector or embedding search.

A repository audit (this experiment's own Stage 1, and separately
recorded in `docs/RFC_ALIGNMENT.md`) found that **no real audio, score,
or subtitle file, and no composer/work-specific critique or theory text,
exists anywhere in this workspace** for any of the 9 target works. Per
the specification's own "do not fabricate" instruction and explicit
direction from the requester, implementation stopped at the design layer:

- `experiments/_observation_bundle.py` — the Observation Bundle data
  model (`Observation`, `ObservationBundle`, `TargetObject`,
  `TargetHierarchy`, `InvariantSignature`) and the typed-morphism
  vocabulary (`acoustically_realizes`, `formally_defines`, `interprets`,
  `documents`, `transcribes`, `creates`, `contains`, `manifests`).
- `experiments/_multimodal_corpus.py` — the 9-work catalog, the real
  corpus directory contract, and `discover_corpus()`, which scans a real
  directory and honestly reports what real files are present (today: 0
  of 45).
- `experiments/_multimodal_extractors.py` — a `Protocol` per modality
  (the extractor *boundary*) plus `reference_extractor`, which always
  raises `NotImplementedError` naming exactly what real file and real
  library/approach a concrete implementation would need, rather than
  returning a fabricated `Observation`.
- `experiments/_cross_modal_reconstruction.py` — the Cross-Modal
  Reconstruction Engine. Adds no new retrieval algorithm: it calls
  `_semantic_closure.compute_closure` (EXP-HEKB002, unmodified) and
  reshapes its real output into the specification's §VI response payload.
- `experiments/exp_hekb_004_multimodal_convergence.py` — orchestrates
  Stage 1 (corpus discovery) and `mechanism_verification`; Phases 1-3 are
  reported as `blocked_on_real_corpus`, not simulated.

## Architectural Findings

- **`_semantic_closure.compute_closure` was reused unmodified**, exactly
  as for EXP-HEKB003. The reconstruction engine's only new logic is
  reshaping its `SemanticClosure` output into the specification's
  Observation Bundle / `proof_path` / `search_metrics` payload shape —
  verified by `dataclasses.asdict` round-tripping every field name to
  match, rather than a hand-maintained mapping that could drift.
- **Morphism direction models the specification's diagram exactly**:
  each modality's morphism points *from* the observation *to* the Target
  Object Q (`Audio --acoustically_realizes--> Q`, etc.), so given Q,
  `compute_closure`'s pushout direction (objects pointing *at* the
  query) is precisely "recover everything that observes Q" — the
  mechanism the Cross-Modal Reconstruction Engine relies on. Verified in
  `mechanism_verification` (below), not merely assumed.
- **The typed-morphism *type* stays a side table (`relation_kind: dict[str, str]`),
  not a new field on `hekb.models.KnowledgeRelation`** — the same
  boundary decision EXP-HEKB002/003 already made, and recorded there;
  extending `src/hekb`'s production model was out of scope then and now.
- **`InvariantSignature.homotopy_hash`/`betti_numbers` stay `None`** —
  `cle.homotopy` (in `categorical-lift-engine`) is still Protocol-only, no
  algorithm exists, so nothing is fabricated to fill either field, exactly
  as EXP-HEKB002/003 already established for this same gap.

## Repository Boundary Findings

- `src/hekb` **not modified** — same 663-line algebraic core as
  EXP-HEKB001-003 left it.
- No Graphify repository exists in this workspace (unchanged since
  EXP-HEKB001) — this experiment did not attempt to invent one; its
  extractor Protocols are reference boundaries, not Graphify.
- No real MCP transport exists (unchanged since EXP-HEKB002) — not
  attempted here either; the reconstruction engine's payload shape is
  designed to be MCP-servable once one exists, but nothing here stands
  one up.
- No real audio, score, subtitle, or composer/work-specific critique/
  theory file exists anywhere in `/media/psf/SSD1TB` for any of the 9
  target works (full search: `.mp3 .wav .musicxml .mid .midi .vtt .mxl
  .xml .srt .flac .opus .m4a`, depth 6). This is the repository boundary
  that stopped Stage 3 short of ingestion.
- meaning-mapper still does not exist as a real package anywhere on this
  machine (unchanged since EXP-HEKB002/003); the established
  `msr.abi.MeaningMeasurement`-stream substitution convention is
  documented as the plan for when real audio/score content is available
  to derive a measurement from, but was not exercised here since no such
  content exists yet.

## Validation Metrics

The specification's 8 target metrics (§III: `R_convergence`,
`Y_bundle`, `F_convergence`, `P_invariant`, `R_reconstruct`,
Target Object Hierarchy Resolution, `C(Q)`, `tau_multimodal`) were **not
measured** — every one of them requires real multi-modal observations
that do not exist in this workspace. Reporting a number for any of them
now would be fabrication, which this experiment was explicitly told not
to do.

What *was* measured, honestly, against the real (empty) corpus directory
and a real, non-musical mechanism-verification fixture:

| Property | Result |
|---|---|
| Real corpus discovery | 0 / 45 observation points present, across all 9 works — a real, honest scan of a real directory |
| Mechanism verification (`MechanismTest_*`, not real music) | Pass — the reconstruction engine correctly recovered both `MechanismTest_ObsA` and `MechanismTest_ObsB` for `MechanismTest_Q` via a real pushout closure, and `SemanticClosure.is_minimal_self_contained` held |
| Reconstruction engine latency (mechanism fixture, 3-object category) | ~0.03ms — real, measured wall-clock time; not comparable to the specification's 45+-object, <15ms-at-p99 target, which requires the real corpus |
| Overall experiment | `"pass": false` — honestly reported; the main objective (real multi-modal convergence) is unmeasured, not failed |

Full output: `experiments/results/exp_hekb_004.json` (copied here as
`results.json`).

## Quality Gates

See the top-level report for exact numbers as run at commit time; `src/hekb`
is unmodified so its own baseline (29 tests, 91% coverage, mypy --strict
clean) is unaffected by this experiment.

## Gap Analysis Summary

| Priority | Finding |
|---|---|
| A (implementation defect) | None found. |
| B (spec doesn't match implementation) | None — the spec's own "Implementation Status" section (added to `specification.md`) documents the scope reduction to design-only. |
| C (architectural decision, open) | Whether audio/score extraction should depend on a real third-party library (e.g. `music21`, `soundfile`, `webvtt-py`) once real files exist, or a from-scratch minimal parser, matching this repository's dependency-light convention (`dependencies = []` in `pyproject.toml`). |
| D (future experiment / architectural gap) | Real audio/score/subtitle/critique corpus for the 9 target works (blocking); real Graphify; real MCP transport; real homotopy algorithm (`cle.homotopy`) — all unchanged, open gaps from EXP-HEKB001-003, none newly introduced here. |

## Lessons Learned

1. **A specification's own worked example (§VI's JSON payload) is not a
   claim that those numbers have been measured.** `specification.md` now
   says so explicitly, to prevent a future reader from mistaking the
   illustrative payload for a validated result.
2. **Designing interfaces before data exists is itself a real,
   verifiable deliverable** — `mechanism_verification`'s abstract,
   explicitly-labeled fixture proves the reconstruction engine's wiring
   (real category, real closure, real pushout direction) independently
   of whether any real musical data has been ingested, the same way
   EXP-HEKB002 validated the closure algorithm itself before EXP-HEKB003
   supplied real data to run it against.
3. **"Blocked" is a distinct, honest outcome from "failed."** This
   report's `"pass": false` reflects an unmeasured objective, not a
   defect in the mechanism — recorded as such rather than glossed over.
