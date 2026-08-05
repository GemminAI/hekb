# EXP-HEKB006: Cross-Model Epistemic Invariance & Multi-LLM Epistemic Convergence Validation

- **Project**: SensOS Core & Enterprise Project / Multi-Modal Epistemic Integration Series
- **Date**: 2026-08-05
- **Version**: 1.0.0
- **Status**: Proposed / Active Specification
- **Target Components**: `meaning-mapper`, `msr`, `cle-core`, `HEKB Storage Engine`, `Semantic Closure Engine`, `Semantic Search Engine`, `HEKB MCP Service`
- **Upstream Sources**:
  1. **Heterogeneous Observers (Multi-LLM Engines)**: Open-Weights Models (Gemma, Qwen, Llama, Mistral) & Proprietary API Models (Claude, GPT, Gemini)
  2. **Multi-Modal Target Corpus**: Visual Art Corpus (`EXP-HEKB005`), Music/Audio Corpus (`EXP-HEKB004`), Software Artifacts (`EXP-HEKB003`)
- **Downstream Target**: Model-Agnostic Epistemic Core, Universal Context Injection, Cross-Model Knowledge Federation

## I. Executive Summary & Rationale

This experiment (**EXP-HEKB006**) builds on the "observation -> semantic
projection -> phase-space trajectory -> categorical lift -> semantic closure
-> observation bundle reconstruction" pipeline established by EXP-HEKB001
through EXP-HEKB005, and asks whether SensOS HEKB can reconstruct a
universal invariant structure **independent of any one large language
model's internal representation or bias** -- Model Invariance & Cross-Model
Epistemic Convergence.

In SensOS, an LLM is not the owner of knowledge but an *observer* $M_k$ of a
shared target object $Q$. Different LLMs $M_k \in \{\text{Gemma, Qwen,
Llama, Mistral, Claude, GPT, Gemini}\}$ may extract different natural
language from the same raw observation; the specification asks whether,
after passing through Meaning Mapper -> MSR -> CLE, they deterministically
converge onto the same invariant signature $\mathbf{S}(Q)$, proof path, and
semantic closure $\mathcal{S}(Q)$.

```
                    [ Observed Target Object Q ]
     +----------------------------+----------------------------+
[ Observer 1: Claude ]   [ Observer 2: Llama ]    [ Observer 3: Gemma ]
     |                            |                            |
     v                            v                            v
[ Meaning Mapper ]        [ Meaning Mapper ]        [ Meaning Mapper ]
     |                            |                            |
     v                            v                            v
[ MSR Trajectory ]        [ MSR Trajectory ]        [ MSR Trajectory ]
     +----------------------------+----------------------------+
                                  |
                                  v
                    [ Categorical Lift Engine ]
                                  |
                                  v
                     [ HEKB Epistemic Graph / Q ]
                                  |
                                  v
              [ Cross-Model Invariance Verification ]
```

## II. Multi-LLM Observation Test Matrix

| Observer Engine | Type | Test Corpora | Task |
|---|---|---|---|
| Gemma | Open Weights | Painting (HEKB005), Music (HEKB004), Specs (HEKB003) | Structural description / region annotation / technique decomposition |
| Qwen | Open Weights | same | same |
| Llama | Open Weights | same | same |
| Mistral | Open Weights | same | same |
| Claude | Proprietary API | same | same |
| GPT | Proprietary API | same | same |
| Gemini | Proprietary API | same | same |

## III. Target Metrics & Acceptance Criteria

1. **Cross-Model Invariant Identity** ($I_{\text{cross\_model}}$) -- Target >= 0.98.
2. **Closure Structure Similarity** ($S_{\text{closure\_sim}}$) -- Jaccard over objects/typed morphisms. Target >= 0.95.
3. **Morphism Graph Edit Distance** ($\text{GED}_{\text{morphism}}$) -- Target <= 0.05 normalized.
4. **Pullback & Pushout Identity Rate** ($R_{\text{limit\_identity}}$) -- Target >= 0.98.
5. **Proof Path Alignment Rate** ($P_{\text{proof\_align}}$) -- Target >= 0.95.
6. **Cross-Model Observation Completeness** ($C_{\text{cross\_obs}}$) -- Var(C_obs) target < 0.005.
7. **Cross-Model Retrieval Latency Variance** ($\tau_{\text{variance}}$) -- Target < 15ms at p99 across all models.

If homotopy or Betti numbers are still unavailable, report "not measurable" -- do not invent values.

## IV. Model Invariance Test Suite

- **Test A (Direct Model Inter-Consistency)**: 7 models, same raw input -> same invariant signature S(Q).
- **Test B (Open-Weights vs Proprietary Invariance)**: local (Gemma/Llama) HEKB graph vs. cloud API (Claude/GPT) HEKB graph, S_closure_sim >= 0.95.
- **Test C (Cross-Model Pullback Derivation)**: two different works' descriptions from two different models converge on the same shared technique node (e.g. Q_Sfumato) via pullback.
- **Test D (Proof Path Equivalence)**: query "Fate_Motif" across model observations -> same structural proof_path.
- **Test E (Model Disambiguation Guard)**: two visually/conceptually distinct targets described by two different models must NOT be merged (F_convergence <= 1.0%).

## V. Phased Execution Matrix

| Phase | Scope | Purpose | Completion Criteria |
|---|---|---|---|
| Phase 1 | 2 models (Gemma vs Claude) x 3 masterworks (HEKB005) | first invariant convergence, I_cross_model | I_cross_model >= 0.98 |
| Phase 2 | 7 models x all corpora | GED_morphism, pullback identity | GED_morphism <= 0.05, R_limit_identity >= 0.98 |
| Phase 3 | Full Test Suite A-E | Var(C_obs), proof_path equivalence | S_closure_sim >= 0.95, P_proof_align >= 0.95, Var(C_obs) < 0.005 |

## VI. Response Payload Schema (illustrative worked example, not a claim of measured values)

```json
{
  "query": {"raw_input": "Sfumato technique in Da Vinci portraits", "target_id": "DaVinci_Sfumato_Technique"},
  "target_object": {
    "id": "DaVinci_Sfumato_Technique",
    "canonical_name": "Sfumato (Contour Dissolution)",
    "invariant_signature": {"homotopy_hash": "e8a912b04f71a...", "betti_numbers": [1, 1, 0]}
  },
  "cross_model_verification": {
    "participating_observers": ["Gemma-2-27b", "Llama-3.1-70b", "Claude-3.5-Sonnet", "GPT-4o", "Gemini-1.5-Pro"],
    "invariant_identity_score": 1.0,
    "closure_structure_similarity": 0.978,
    "morphism_graph_edit_distance": 0.021,
    "proof_path_alignment": 0.985
  }
}
```

## VII. Revision History

- 2026-08-05: v1.0.0 -- initial 7-engine multi-LLM observer matrix, Cross-Model Invariant Identity, Graph Edit Distance, Proof Path Alignment, Tests A-E.

---

## Implementation Instructions (as supplied with this specification)

Same engineering policy as EXP-HEKB001-005. This experiment follows the
honesty and repository-boundary rules established by EXP-HEKB001-005:

1. Do not modify `src/hekb` unless a genuine production bug is discovered.
2. Implement everything under `experiments/`.
3. Reuse existing code whenever possible -- in particular `_semantic_closure.py`,
   Semantic Search, Observation Bundle, Visual reconstruction, existing HEKB
   storage, and existing experiment utilities must be reused instead of
   rewritten. No duplicate implementations.
4. Use real observers whenever available (local models first: Gemma, Qwen,
   Llama, Mistral; then API models: Claude, GPT, Gemini). If a model cannot
   be executed in this environment: **do not fabricate outputs**. Report it
   honestly, mark the observer unavailable, and continue with available
   observers.
5. Reuse real corpora from EXP-HEKB003/004/005. Do not create synthetic
   artworks or fake documents.
6. Compare only HEKB structures -- never compare raw generated text. Measure
   invariant identity, closure similarity, proof path alignment, morphism
   graph edit distance, pullback identity, pushout identity, retrieval
   determinism. If homotopy or Betti numbers are still unavailable, report
   "not measurable" -- never invent values.
7. Only report metrics actually computed. If a metric cannot be measured
   because a required component does not exist, explicitly say `NOT
   MEASURED`. Never estimate.
8. Quality gates (pytest, coverage, ruff, ruff format, mypy --strict) must
   all pass without reducing the existing baseline before commit.
9. Do not commit automatically -- report Architectural Findings, Repository
   Boundary Findings, Validation Metrics (Measured / Not Measured /
   Blocked, for every metric), Quality Gates, Changed Files, and Remaining
   Future Work, and wait for approval.

## Implementation Status (added 2026-08-05, post-commissioning)

A real environment probe (`experiments/_observer_adapter.py`,
`probe_observer_availability`) found **0 of the 7 named observer engines
callable in this workspace**: no local model runtime (`ollama` binary not
on `PATH`; `llama_cpp` not importable) for Gemma/Qwen/Llama/Mistral, and no
API credential (`ANTHROPIC_API_KEY`/`OPENAI_API_KEY`/`GOOGLE_API_KEY`/
`GEMINI_API_KEY`) for Claude/GPT/Gemini. Per this specification's own "DO
NOT fabricate outputs" instruction, no observer text was invented, and
every metric in section III is reported `NOT MEASURED` with the specific
real reason it requires.

What *was* built and is real:

- `experiments/_observer_adapter.py` -- the `ObserverAdapter` Protocol
  boundary plus a real, re-runnable availability probe (would honestly
  detect a newly pulled Ollama model or a newly exported API key without
  any code change).
- `experiments/_cross_model_runner.py` -- per-observer call orchestration;
  every call attempt raises a `NotImplementedError` naming exactly which
  package/API a concrete integration would need, mirroring
  `_multimodal_extractors.py`'s convention exactly. No text is fabricated.
- `experiments/_cross_model_compare.py` -- the real, new comparison engine:
  `closure_structure_similarity`, `morphism_graph_edit_distance`,
  `pullback_pushout_identity_rate`, `proof_path_alignment`,
  `invariant_identity`, `completeness_variance`, `latency_variance_ms` --
  every function operates on `_semantic_closure.SemanticClosure` (EXP-HEKB002,
  reused unmodified) or a supplied `proof_path`; no new retrieval algorithm.
- `experiments/exp_hekb_006_cross_model.py` -- orchestrates Stage 1 (real
  observer availability), Stage 2 (real inventory of the EXP-HEKB003/004/005
  corpora already prepared for future cross-model ingestion), Stage 3
  (real, honest per-observer call attempts), Stage 4 (an abstract
  `MechanismTest_*`-labeled mechanism-correctness check of the comparison
  engine itself), and reports every specification section III metric as
  `NOT MEASURED`, every Phase (V) and Test (IV) as `blocked_on_real_observers`.

See `report.md` for full findings.

Quality gates before commit: pytest, coverage, ruff check, ruff format
--check, mypy --strict. Do not commit automatically -- wait for approval.

---

## v2.1.0 Reframing: Observer Invariance & the Reality Consensus Engine (added 2026-08-05)

A revised specification (v2.1.0, supplied externally as "Observer
Invariance, Epistemic Agnosticism & Reality-Driven Multi-Observer
Convergence Validation") reframes this experiment's primary objective:

> The primary objective of EXP-HEKB006 is NOT comparing LLMs. The primary
> objective is constructing a model-agnostic Reality Consensus Engine.

Rather than "do 7 LLMs converge on the same structure" (v1.0.0, above),
v2.1.0 asks whether a **Pullback Limit over typed morphisms** --
$S_{\text{consensus}}(Q) = \varprojlim_k S(Q)^{(M_k)}$ -- can be
constructed and verified as a real, working mechanism, and whether a real
**Human Ground Truth** (Phase 1, before any AI observer) can be built from
independently-authored sources already in this workspace's real corpora.
v2.1.0 explicitly instructs: "Observer APIs are optional... execute all
deterministic mechanisms, execute all Human-vs-Human consensus tests,
execute all Reality Consensus tests, execute all registry and capability
discovery... and report only the unavailable observer-dependent metrics
as BLOCKED."

### What changed vs. v1.0.0

- **New**: `_reality_consensus.py` -- the Reality Consensus Engine itself:
  an N-way (not just pairwise) pullback-limit consensus, Observer Bias
  Index (OBI), leave-one-out robustness, blind-anonymization invariance,
  and a false-convergence guard. Pure set arithmetic over already-computed
  `_semantic_closure.SemanticClosure` values -- no new retrieval
  algorithm, no vector or embedding search, exactly the same honesty
  contract `_cross_model_compare.py` (v1.0.0) already established.
- **New**: `_human_observers.py` -- Phase 1's real Human-vs-Human ground
  truth. This workspace has no live human-expert panel, but EXP-HEKB005's
  real corpus already contains 3 independently-authored real channels for
  the same real target objects: `critique.md` (a named human critic --
  Vasari / EB1911 / van Gogh's own letters), `wiki.md` (Wikipedia's
  editorial community), and `catalog.json` (Wikidata's curatorial
  metadata). Treating each channel as one "Human Observer" and building a
  separate real closure per channel is a re-partitioning of already-real,
  already-ingested data, not fabrication -- no new corpus is fetched, no
  text is generated.
- **New**: `_observer_registry.py` -- a unified registry spanning both
  the real human-channel plane and the 7 named LLM engines
  (`_observer_adapter.py`, v1.0.0, reused unmodified).
- **New**: `exp_hekb_006_reality_consensus.py` -- the v2.1.0 orchestrator,
  implementing Phases 1-4 and Tests A-J, embedding v1.0.0's
  `exp_hekb_006_cross_model.run()` output whole (as
  `cross_model_observer_plane_v1_0_0`) rather than re-deriving the
  0/7-observer finding.
- **Unchanged, reused**: `_semantic_closure.compute_closure`
  (EXP-HEKB002), `_cross_model_compare.proof_path_alignment`,
  `_visual_reconstruction.find_shared_technique_terms`, every
  EXP-HEKB005 extractor, and `_observer_adapter.probe_observer_availability`
  (still 0/7 named LLM engines callable -- this real finding has not
  changed).

### Honest scope of Tests A-J under v2.1.0

The specification's Test G wants >= 5 independent observers; this
workspace's real human plane provides at most 3 (Critique + Wiki +
MuseumCatalog) per work, since 0/7 named LLM engines remain callable.
Tests B and H are specifically AI-observer-plane tests (open-weights vs.
proprietary; AI-consensus vs. human ground truth) and are reported
`BLOCKED` for that same real reason -- never estimated, never defaulted to
a passing value. See `report.md` for the full per-test disposition and
`results.json` for every measured number.
