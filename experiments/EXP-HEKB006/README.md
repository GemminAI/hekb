# EXP-HEKB006: Observer Invariance & the Reality Consensus Engine

## Status (v2.1.0, current)

**Measured and passing on the real human-observer plane; the AI-observer
plane remains honestly BLOCKED (0/7 named LLM engines callable).** Per
the v2.1.0 specification's own scope decision ("Observer APIs are
optional... execute all deterministic mechanisms... report only the
unavailable observer-dependent metrics as BLOCKED"), this experiment
does not stop at LLM unavailability: the Reality Consensus Engine
(`_reality_consensus.py`), a real Phase 1 Human-vs-Human Ground Truth
(`_human_observers.py`, built from 3 independently-authored real channels
already in EXP-HEKB005's corpus), the Observer Registry
(`_observer_registry.py`), and Tests A/C/D/E/F/G(partial)/I/J are all
measured on real data. Tests B and H, and Test G's >= 5-observer target,
remain `BLOCKED` for the same real, unchanged reason v1.0.0 (below)
already found. See `report.md`'s "v2.1.0 Addendum" for full findings and
`results.json` for every number.

## Status (v1.0.0, superseded framing — retained below)

**Design/mechanism-stage only, implementation paused on observer access.**
Not a completed, measured cross-model experiment like EXP-HEKB003/005 —
see `report.md` for why. Reused unmodified by v2.1.0's orchestrator as
`cross_model_observer_plane_v1_0_0` — this finding is embedded, not
discarded.

## Purpose

Demonstrate that 7 named LLM observer engines (Gemma, Qwen, Llama,
Mistral, Claude, GPT, Gemini), after passing through Meaning Mapper -> MSR
-> CLE, converge onto the same HEKB invariant structure for a shared
target object — measured via closure structure similarity, morphism graph
edit distance, pullback/pushout identity, and proof path alignment (no
vector or embedding search).

## Target Repository

`/media/psf/SSD1TB/HEKBv2`.

## Target Specification

EXP-HEKB006 v1.0.0 (full text in `specification.md`).

## Why this is paused

A real environment probe found 0 of the 7 named observer engines callable
in this workspace: no local model runtime (`ollama`, `llama_cpp`) for
Gemma/Qwen/Llama/Mistral, and no API credential
(`ANTHROPIC_API_KEY`/`OPENAI_API_KEY`/`GOOGLE_API_KEY`/`GEMINI_API_KEY`)
for Claude/GPT/Gemini. Per the specification's own "do not fabricate"
instruction, implementation stopped at the design/mechanism layer, the
same choice EXP-HEKB004 made when its real corpus was absent.

## What exists today

- `experiments/_observer_adapter.py` — the `ObserverAdapter` Protocol plus
  `probe_observer_availability`, a real, re-runnable environment check.
- `experiments/_cross_model_runner.py` — per-observer call orchestration;
  every attempt honestly fails with a specific, named reason. No
  fabricated text anywhere.
- `experiments/_cross_model_compare.py` — the new Cross-Model Comparison
  Engine (closure similarity, graph-edit-distance proxy, pullback/pushout
  identity, proof-path alignment, invariant identity, completeness/latency
  variance), built entirely on EXP-HEKB002's `_semantic_closure.compute_closure`,
  reused unmodified.
- `experiments/exp_hekb_006_cross_model.py` — orchestrator: real observer
  availability (Stage 1), real inventory of EXP-HEKB003/004/005's
  existing corpora (Stage 2), real per-observer call attempts (Stage 3),
  and an abstract `MechanismTest_*` mechanism-correctness check of the
  comparison engine (Stage 4) — every specification metric/phase/test is
  reported `NOT MEASURED` / `blocked_on_real_observers`.

## What exists today (v2.1.0 addition)

- `experiments/_reality_consensus.py` — the Reality Consensus Engine: a
  Pullback Limit (K-way intersection of typed morphisms) over any number
  of real `_semantic_closure.SemanticClosure` values, plus Observer Bias
  Index, leave-one-out robustness, blind-anonymization invariance, and a
  false-convergence guard. Pure set arithmetic; no new retrieval, no
  vector/embedding search.
- `experiments/_human_observers.py` — Phase 1's real Human-vs-Human
  Ground Truth: 3 independently-authored real channels
  (`critique.md`/`wiki.md`/`catalog.json`) already in EXP-HEKB005's real
  corpus, re-partitioned into 3 separate real per-channel closures.
- `experiments/_observer_registry.py` — a unified registry of both the
  real human-channel plane and the 7 named LLM engines
  (`_observer_adapter.py`, reused unmodified).
- `experiments/exp_hekb_006_reality_consensus.py` — the v2.1.0
  orchestrator (Phases 1–4, Tests A–J), embedding v1.0.0's
  `exp_hekb_006_cross_model.run()` output whole rather than re-deriving
  the still-real 0/7-LLM finding.

## Reproduction

```bash
cd /media/psf/SSD1TB/HEKBv2
source .venv/bin/activate
cd experiments
python exp_hekb_006_reality_consensus.py   # current, v2.1.0 -- writes results/exp_hekb_006.json
python exp_hekb_006_cross_model.py         # v1.0.0 cross-model plane, standalone, still runnable
```

Results land in `experiments/results/exp_hekb_006.json` (`"pass": true` —
every measurable mechanism/consensus check on the real human plane
passes; this does not require the AI-observer plane, by design. See
`report.md`'s "v2.1.0 Addendum" for the full metric table).

## Quality Gates

```bash
cd /media/psf/SSD1TB/HEKBv2
source .venv/bin/activate
python -m pytest -q
ruff check .
ruff format --check .
python -m mypy .
```

See `report.md`'s Quality Gates section for the exact current pass/fail
counts.

## Next steps

Real access to at least 2 of the 7 named observer engines (a local Ollama
pull or an exported API key would be honestly detected by
`probe_observer_availability` with no code change), a real Meaning Mapper
(would unblock ingestion once observer text exists), a real
`cle.homotopy` implementation (would unblock `I_cross_model` specifically),
and real access to a genuine human-expert panel (distinct from the
existing corpus's own already-real channels, for Test H) are all recorded
as open architectural gaps in `report.md`, not attempted here.
