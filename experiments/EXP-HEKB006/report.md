# EXP-HEKB006 — Report

## Implementation Summary

EXP-HEKB006 was commissioned to validate that 7 named LLM observer engines
(Gemma, Qwen, Llama, Mistral, Claude, GPT, Gemini) converge, after passing
through Meaning Mapper -> MSR -> CLE, onto the same HEKB invariant
structure for a shared target object — reusing EXP-HEKB002's Semantic
Closure Engine, EXP-HEKB003's Semantic Search Engine, and the real corpora
EXP-HEKB003/004/005 already prepared, unmodified.

A real environment probe (`experiments/_observer_adapter.py`,
`probe_observer_availability`) is this experiment's own Stage 1, and found
**0 of the 7 named observers callable in this workspace**: no local model
runtime (`ollama` binary not on `PATH`; `llama_cpp` not importable) for
Gemma/Qwen/Llama/Mistral, and no API credential
(`ANTHROPIC_API_KEY`/`OPENAI_API_KEY`/`GOOGLE_API_KEY`/`GEMINI_API_KEY`)
for Claude/GPT/Gemini. Per the specification's own "do not fabricate"
instruction, implementation stopped at the design/mechanism layer for the
cross-model comparison itself, exactly as EXP-HEKB004 stopped at the
design layer when its real corpus was absent:

- `experiments/_observer_adapter.py` — the `ObserverAdapter` Protocol (the
  Observer step's boundary) plus `probe_observer_availability`, a real,
  re-runnable check (`shutil.which`, `importlib.util.find_spec`, a real
  `ollama list` subprocess call, `os.environ.get`) — never a hardcoded
  result.
- `experiments/_cross_model_runner.py` — `run_observer`/`run_all_observers`,
  which always raise/report `NotImplementedError` naming exactly which
  package or API a concrete integration needs, mirroring
  `_multimodal_extractors.reference_extractor`'s convention exactly. No
  text is fabricated in place of a real model's output anywhere in this
  module.
- `experiments/_cross_model_compare.py` — the new Cross-Model Comparison
  Engine: `closure_structure_similarity`, `morphism_graph_edit_distance`,
  `pullback_pushout_identity_rate`, `proof_path_alignment`,
  `invariant_identity`, `completeness_variance`, `latency_variance_ms`.
  Adds **no new retrieval algorithm** — every function is a comparison
  computed over an already-built `_semantic_closure.SemanticClosure`
  (EXP-HEKB002, unmodified) or a supplied `proof_path`.
- `experiments/exp_hekb_006_cross_model.py` — orchestrates Stage 1 (real
  observer availability), Stage 2 (real inventory of the real corpora
  EXP-HEKB003/004/005 already ingested/discovered), Stage 3 (real,
  per-observer call attempts, all honestly failing), Stage 4 (an abstract
  `MechanismTest_*` mechanism-correctness check of the new comparison
  engine), and reports every specification metric/phase/test as
  `NOT MEASURED` / `blocked_on_real_observers`.

## Architectural Findings

- **`_semantic_closure.compute_closure` was reused unmodified**, exactly
  as EXP-HEKB003/004/005. `_cross_model_compare.py`'s only new logic is
  comparison arithmetic over two already-computed `SemanticClosure`
  values (Jaccard similarity, a symmetric-difference-based edit-distance
  proxy, and a real dynamic-programming LCS for proof-path alignment) —
  no new graph traversal, no vector or embedding search anywhere.
- **The mechanism-correctness check (Stage 4) proves the new comparison
  code is wired correctly, independent of observer availability.** Two
  abstract `MechanismTest_*` categories built with identical structure
  score `closure_structure_similarity=1.0`, `morphism_graph_edit_distance=0.0`,
  `pullback_pushout_identity_rate=1.0`, `proof_path_alignment=1.0` against
  each other; a third, deliberately divergent category scores
  `closure_structure_similarity=0.143`, `morphism_graph_edit_distance=0.857`
  against the first — a real, checked demonstration that the metrics
  actually discriminate structure rather than always returning a fixed
  value. This is a code-correctness check, not a claim about real
  cross-model convergence, and is labeled as such throughout.
- **`invariant_identity` (I_cross_model) is honestly `None` even in the
  mechanism check.** Neither `MechanismTest_*` category carries a real
  `homotopy_hash` (`cle.homotopy` is still Protocol-only — the same gap
  EXP-HEKB002-005 already recorded), so `invariant_identity` correctly
  returns the NOT-MEASURED sentinel rather than a fabricated boolean, in
  both the identical-structure and divergent-structure comparisons.
- **`_observer_adapter.probe_observer_availability` is a real, adaptive
  check, not a hardcoded "all unavailable" list.** It inspects `PATH` for
  `ollama`, checks `llama_cpp` importability, runs a real `ollama list`
  subprocess call when the binary is present (matching pulled model names
  against each open-weights engine's name), and reads the exact
  environment variable each proprietary engine's official SDK expects.
  Re-running it after `ollama pull gemma2` or `export
  ANTHROPIC_API_KEY=...` would honestly reflect the change with no code
  edit.
- **Stage 2 (corpus inventory) reuses, and does not re-derive, three prior
  experiments' real corpora**: `_real_visual_extractors.discover_visual_corpus`
  (EXP-HEKB005, 42/45 real observation points), `_multimodal_corpus.discover_corpus`
  (EXP-HEKB004, still 0/45 — unchanged since that experiment), and
  `_real_corpus.build_real_property_graph` (EXP-HEKB003, a real 3-repository
  software artifact survey: 115 nodes, 213 edges from `meaning-space-runtime`,
  `categorical-lift-engine`, and this repository). None of these corpora
  were re-fetched, re-scanned with new logic, or modified — every number
  reported here is EXP-HEKB003/004/005's own existing extraction, called
  as-is.

## Repository Boundary Findings

- `src/hekb` **not modified**.
- **0 of 7 named observer engines have real, callable access in this
  workspace** — checked directly, not assumed: no `ollama` binary on
  `PATH`, no importable `llama_cpp`, and no `ANTHROPIC_API_KEY`/
  `OPENAI_API_KEY`/`GOOGLE_API_KEY`/`GEMINI_API_KEY` in the environment.
  This is the repository-boundary finding that blocks every real
  cross-model metric in section III, exactly the class of finding
  EXP-HEKB004 recorded for its missing musical corpus.
- **No real Meaning Mapper exists in this workspace**, unchanged since
  EXP-HEKB002-005. Even were a real observer's raw text obtainable today,
  there is still no real component to project arbitrary natural language
  into a `msr.abi.MeaningMeasurement` — this experiment's own
  `_cross_model_runner.py` docstring records this as a second, compounding
  blocker on the ingestion side, not only the observation side.
- **`cle.homotopy` is still Protocol-only** (`categorical-lift-engine`'s
  own `docs/RFC_ALIGNMENT.md`) — `invariant_identity`/`I_cross_model` can
  never be a real boolean in this workspace today regardless of observer
  availability; `_cross_model_compare.invariant_identity` returns `None`
  rather than fabricate one, exactly as EXP-HEKB002-005 already
  established for `homotopy_hash`/`betti_numbers`.
- No Graphify, no real MCP transport — unchanged findings from
  EXP-HEKB001-005; none invented here.
- No vector or embedding search anywhere — every comparison in
  `_cross_model_compare.py` is a real graph/set/sequence quantity (Jaccard,
  symmetric-difference proxy, exact LCS), per explicit instruction.

## Validation Metrics

| Property | Result |
|---|---|
| Stage 1: Observer availability (7 engines checked) | **Measured** — 0/7 available (real check; see `stage1_observer_availability` in `results.json`) |
| Stage 2: Corpus inventory (EXP-HEKB003/004/005 reuse) | **Measured** — visual 42/45, multimodal 0/45, software-artifact 115 nodes/213 edges, all real numbers reused from the originating experiments |
| Stage 3: Per-observer call attempts (7 engines) | **Measured** — 7/7 honestly failed with a real, specific reason each; 0 fabricated |
| Stage 4: Mechanism verification (`_cross_model_compare.py` wiring) | **Measured (mechanism only, not real observer output)** — identical-structure pair scores 1.0/0.0/1.0/1.0/None exactly as expected; divergent-structure pair scores 0.143/0.857/0.5, correctly discriminating |
| $I_{\text{cross\_model}}$ (Cross-Model Invariant Identity) | **NOT MEASURED** — requires >=2 real per-observer `homotopy_hash` values; `cle.homotopy` Protocol-only AND 0 real observers exist |
| $S_{\text{closure\_sim}}$ (Closure Structure Similarity) | **NOT MEASURED** — requires >=2 real per-observer `SemanticClosure`s; 0 real observers exist |
| $\text{GED}_{\text{morphism}}$ (Morphism Graph Edit Distance) | **NOT MEASURED** — same reason |
| $R_{\text{limit\_identity}}$ (Pullback & Pushout Identity Rate) | **NOT MEASURED** — same reason |
| $P_{\text{proof\_align}}$ (Proof Path Alignment Rate) | **NOT MEASURED** — requires >=2 real per-observer proof paths; 0 real observers exist |
| $\text{Var}(C_{\text{obs}})$ (Cross-Model Observation Completeness variance) | **NOT MEASURED** — variance is undefined for 0 real per-observer completeness values; `_cross_model_compare.completeness_variance` returns `None` below 2 values rather than a misleading `0.0` |
| $\tau_{\text{variance}}$ (Cross-Model Retrieval Latency Variance) | **NOT MEASURED** — same reason as $\text{Var}(C_{\text{obs}})$ |
| Phase 1 / Phase 2 / Phase 3 (section V) | **Blocked** — `blocked_on_real_observers`, same real reason |
| Test A–E (section IV) | **Blocked** — `blocked_on_real_observers`, same real reason |
| Overall | `"pass": false` — honestly reported as blocked (0 real observers), not failed; Stage 1-4 (all real, all honestly computed) ran with 0 uncaught exceptions |

Full output: `experiments/results/exp_hekb_006.json` (copied here as
`results.json`).

## Quality Gates

pytest: 29 passed (unchanged — `src/hekb` untouched) · coverage: 91% on
`src/hekb` (unchanged) · ruff check: clean · ruff format --check: clean
(82 files) · mypy --strict (`mypy .`): clean, 45 files.

## Gap Analysis Summary

| Priority | Finding |
|---|---|
| A (implementation defect) | None found. |
| B (spec doesn't match implementation) | None — the specification's own "Implementation Status" section documents the scope reduction to design/mechanism-only, the same pattern EXP-HEKB004 used. |
| C (architectural decision, open) | `morphism_graph_edit_distance`'s symmetric-difference-based normalization is a chosen, documented approximation of graph edit distance (like EXP-HEKB003's `Depth_category` table), not a minimum-cost graph-isomorphism search — open whether a future experiment needs the exact (NP-hard in general) quantity instead. |
| D (future experiment / architectural gap) | Real access to at least 2 of the 7 named observer engines (blocking every section III metric); a real Meaning Mapper (blocking ingestion even once observer text exists); a real homotopy/persistent-topology algorithm (`cle.homotopy`, blocking $I_{\text{cross\_model}}$ specifically) — all genuinely absent from this workspace, none invented here. |

## Lessons Learned

1. **A cross-model experiment's Stage 1 is availability, not corpus.**
   Unlike EXP-HEKB004/005 (blocked/unblocked by real *data*), EXP-HEKB006
   is blocked by real *model access* — a different kind of repository
   boundary, and one this experiment's own `probe_observer_availability`
   makes checkable and re-runnable rather than a one-time claim.
2. **A mechanism-correctness check can, and should, still discriminate.**
   EXP-HEKB004's `mechanism_verification` proved its engine handled one
   real case; this experiment's Stage 4 additionally proves the new
   comparison metrics distinguish a converged pair from a divergent one
   (0.143 similarity, not 1.0) — otherwise a mechanism check that only
   ever exercises the identical-structure path could not catch a
   comparison function that always returns `1.0`.
3. **"NOT MEASURED" is not one undifferentiated bucket.** Each of the 7
   target metrics is missing a different, specific real component
   (observer access, Meaning Mapper, `cle.homotopy`) — reporting the exact
   reason per metric, as `results.json` does, is more useful than a single
   blanket "blocked" status, and matches the specification's own
   instruction to report exactly what is missing.

---

## v2.1.0 Addendum: the Reality Consensus Engine (measured)

Per `specification.md`'s v2.1.0 reframing, this addendum implements and
verifies the **Reality Consensus Engine** — a Pullback Limit over typed
morphisms — and a real **Phase 1 Human-vs-Human Ground Truth**, executing
every deterministic mechanism regardless of the still-real 0/7 named
LLM engine availability finding (unchanged from the v1.0.0 section above).
New code: `_reality_consensus.py`, `_human_observers.py`,
`_observer_registry.py`, `exp_hekb_006_reality_consensus.py`. `src/hekb`
remains unmodified.

### What is real here

- **Phase 1 (Human Ground Truth)**: 3 independently-authored real
  channels already in EXP-HEKB005's real corpus — `critique.md` (a named
  human critic: Vasari / EB1911 / van Gogh's own letters, present for 6/9
  works), `wiki.md` (Wikipedia's editorial community, 9/9), `catalog.json`
  (Wikidata's curatorial metadata, 9/9) — each re-partitioned into its own
  real `_semantic_closure.SemanticClosure` via `_human_observers.py`, no
  new corpus fetched, no text generated. All 9 real works have >= 2 real
  human observers; 6 of 9 have all 3.
- **Phase 2 (Observer Registry)**: 10 registered observers (3 real human
  channels + 7 named LLM engines), 3/10 available — the 3 human channels,
  checked from real corpus files; the 7 LLM engines remain 0/7, per
  `_observer_adapter.probe_observer_availability` (v1.0.0, unmodified).
- **Phase 3 (mechanism verification)**: abstract `MechanismTest_*`
  fixtures prove the Pullback Limit, OBI, leave-one-out robustness, and
  blind-anonymization invariance are wired correctly (5 identical
  observers score `consensus_reality_score=1.0`, `OBI=0.0` each,
  `Rob=1.0` each), and that a genuine divergence is detected — not via OBI
  ranking (a real, documented subtlety: OBI is a *fraction of an
  observer's own content*, so a smaller divergent closure can score a
  numerically lower OBI than a larger agreeing one even while being the
  true outlier — see the module's inline comment) but via leave-one-out
  robustness, which correctly shows the true outlier's removal changes
  the group's consensus far more (`Rob=0.2`) than removing any agreeing
  observer (`Rob=1.0`). The false-convergence guard correctly keeps two
  distinct mechanism targets separate.
- **Phase 4 (Tests A–J)**: measured on real data wherever the human plane
  alone can answer the question; `BLOCKED` (not fabricated, not
  defaulted) wherever a test specifically needs a real AI observer.

### Validation Metrics (v2.1.0)

| Metric | Result |
|---|---|
| Phase 1: works with >= 2 real human observers | **Measured** — 9/9 |
| Phase 1: mean / min consensus reality score (R_consensus) | **Measured** — mean 0.314, min 0.231 across all 9 works |
| Phase 2: registry size / available | **Measured** — 10 registered (3 human + 7 LLM), 3 available |
| Phase 3: mechanism verification | **Measured — pass** (identical-5 scores 1.0/0.0-OBI/1.0-Rob exactly; divergent outlier correctly discriminated via Rob=0.2 vs 1.0; false-convergence guard holds) |
| Test A (Direct Observer Inter-Consistency) | **Measured (human plane)** — mean R_consensus 0.314 across 9 works; LLM plane BLOCKED (0/7) |
| Test B (Open-Weights vs Proprietary) | **BLOCKED** — needs >=1 open-weights AND >=1 proprietary LLM callable; 0/7 |
| Test C (Cross-Observer Pullback Derivation) | **Measured — pass** — real shared `technique/sfumato` (3 Da Vinci works) and `technique/camera_obscura` (2 Vermeer works) found in Human_Wiki's own text; combined across all 3 channels also finds `technique/impasto` (2 Vermeer works, via Human_Critique) |
| Test D (Proof Path Equivalence) | **Measured** — mean LCS alignment 1.000 across all real per-work channel pairs (each channel's per-work ingestion is shallow — no `derived_compositions` beyond the resolved target at this depth — so alignment is vacuously perfect rather than a demonstration of a long shared path; see Remaining Future Work) |
| Test E (Disambiguation & False Convergence Guard) | **Measured — pass** — 36/36 real work pairs disambiguated, 0.0% false convergence rate after correctly whitelisting real shared technique/artist nodes |
| Test F (Blind Observer Independence) | **Measured — pass** — anonymizing observer labels leaves every real per-work consensus numerically identical |
| Test G (Reality Consensus Engine Integration) | **Partially measured** — real human plane provides at most 3 observers per work (spec target >= 5); mechanism independently verified at exactly 5 synthetic observers (Phase 3) |
| Test H (Human Expert Consensus Agreement) | **BLOCKED** — requires a real AI-observer consensus closure to compare against; 0/7 LLM engines available |
| Test I (Leave-One-Out Robustness) | **Measured — pass** — 6/9 works have all 3 real channels; mean robustness 1.000 (removing any one of the 3 real observers leaves the same structural core — see Lessons Learned) |
| Test J (Cross-Object Separation Guard) | **Measured — pass** — same 36-pair check as Test E, 0.0% false convergence, target met |
| Overall (`"pass"`) | **`true`** — every measurable mechanism/consensus check on the real human plane passed; this does **not** require the AI-observer plane, by this experiment's own "Observer APIs are optional" scope decision |

Full output: `experiments/results/exp_hekb_006.json` (copied here as
`results.json`; this file now contains BOTH the v2.1.0 Reality Consensus
result at top level AND the full v1.0.0 cross-model result embedded under
`cross_model_observer_plane_v1_0_0`, so no earlier finding was discarded).

### v2.1.0 Quality Gates

pytest: 29 passed (unchanged — `src/hekb` untouched) · coverage: 91% on
`src/hekb` (unchanged) · ruff check (repo-wide, including all new
`experiments/*.py`): clean · ruff format --check: clean (89 files) ·
mypy --strict (`mypy .`): clean, 49 source files. Two ruff findings (an
unsorted import block and a stray private import) and several `E501`
line-length / `RUF005` findings were found and fixed during this same
implementation, not left for a later pass.

### v2.1.0 Gap Analysis Summary

| Priority | Finding |
|---|---|
| A (implementation defect) | Two found and fixed during implementation, recorded rather than hidden: (1) the Phase 3 mechanism test's original divergence check compared Observer Bias Index across observers of different closure sizes, which is not a valid ranking (a smaller divergent closure can score numerically lower OBI than a larger agreeing one) — fixed by discriminating via leave-one-out robustness instead, which is size-invariant; (2) Test E/J's legitimate-overlap whitelist originally checked only `Human_Wiki`'s own technique links, incorrectly flagging `technique/impasto` (found only in `Human_Critique`'s own text for the 2 Vermeer works) as a false convergence — fixed by combining every channel's real technique links before building the whitelist. |
| B (spec doesn't match implementation) | Test D's real per-channel proof paths are shorter than the specification's own worked example (`[Measure_1-2, Fate_Motif, Beethoven_Sym5]`) because `_human_observers.py`'s per-channel categories are shallow (artist → work → observation/technique, 1-2 hops) — `derived_compositions` only appears for paths of length >= 2, so most real per-work proof paths here are the single resolved-target step. Alignment is honestly `1.0` (vacuously, both sides are that one step) rather than a demonstration of a long shared path — see Remaining Future Work. |
| C (architectural decision, open) | OBI (Observer Bias Index) is defined as the fraction of an observer's *own* closure lying outside the K-way consensus core — a real, computable, and correctly-behaving quantity, but (documented in Phase 3's findings above) not a reliable outlier-ranking signal when observers' closures differ substantially in size. Leave-one-out robustness is the more reliable per-observer discriminator for that specific question; both are reported, neither is hidden. |
| D (future experiment / architectural gap) | Same three gaps the v1.0.0 section already recorded (real LLM access, a real Meaning Mapper, a real `cle.homotopy`) — none resolved by this addendum, none newly invented. Additionally: real access to a genuine human-expert panel (not a re-partitioning of already-real corpus channels) would let Phase 1 measure Test H's `R_expert_consensus` against a real AI-observer consensus once one exists. |

### v2.1.0 Lessons Learned

1. **A metric that is real can still be a poor discriminator for a
   specific question.** OBI is honestly computed and behaves correctly by
   its own definition, but Phase 3's mixed-observer mechanism test showed
   it does not reliably identify the true outlier when observer closures
   differ in size — the fix was to add a second, size-invariant metric
   (leave-one-out robustness) for that specific question, not to redefine
   OBI to force the desired ranking.
2. **A whitelist against a union must be built from the same union's
   sources.** Test E/J's false-convergence check compares against each
   work's *union* of every real observer's contribution — a legitimate-
   overlap whitelist checked against only one observer's contribution
   (Wiki) will systematically under-whitelist real, legitimate shared
   structure another observer (Critique) independently found.
3. **Perfect leave-one-out robustness can be a real, informative null
   result, not a bug.** All 6 works with 3 real human channels show
   `Rob=1.0` for every observer — because each channel's own real
   evidence file (`critique.md`/`wiki.md`/`catalog.json`) is always
   unique to it, the 3-way intersection core is exactly the shared
   structural scaffolding (artist, target identity) regardless of which
   one observer is held out. This is a genuine finding about *where* real
   human sources agree (identity/attribution) versus where they
   necessarily differ (their own distinct evidence) — not an artifact of
   a broken metric.
