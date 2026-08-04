# EXP-HEKB004: Multi-Modal Target Ingestion, Invariant Convergence & Cross-Subject Retrieval Validation

- **Project**: SensOS Core & Enterprise Project / Multi-Modal Epistemic Integration Series
- **Date**: 2026-08-05
- **Version**: 1.3.0 (Cross-Modal Reconstruction & Observation Bundle Recovery Expansion)
- **Status**: Proposed / Active Specification — implementation paused pending real corpus (see "Implementation Status" below)
- **Target Components**: `meaning-mapper`, `msr`, `cle-core`, `HEKB Storage Engine`, `Semantic Closure Engine`, `Semantic Search Engine`, `HEKB MCP Service`
- **Upstream Sources**: Audio (`.mp3`/`.wav`), Score (MusicXML/`.mid`), Theory Spec (`.md`), Critiques/Papers (`.md`), Subtitles (`.vtt`)
- **Test Corpus**: 3 Composers x 3 Works (9 Observed Target Objects Q, 45+ Observation Points)
- **Downstream Target**: Multi-Modal Context Economy Injection, Cross-Subject Invariant Search Client

## I. Executive Summary & Rationale

EXP-HEKB004 builds on EXP-HEKB001 (persistence), EXP-HEKB002 (closed-loop
validation), and EXP-HEKB003 (real-world semantic search) to demonstrate
SensOS's Multi-Observation Epistemic Convergence and the bidirectional
reconstruction of an Observation Bundle O(Q).

Unlike vector/embedding joint-embedding approaches (e.g. CLIP), modality
integration in SensOS is defined as: heterogeneous observations O^(m)_t of
an underlying Observed Target Object Q are reconstructed into the same
invariant signature S(Q) via typed morphisms and limit (pullback)
algebra — never via forced vector-space alignment.

To avoid overfitting to a single work or form, the corpus is 3 composers x
3 works x 5 modalities (45+ observation points). Heterogeneous observation
data must converge deterministically to the same invariant signature S(Q)
via typed morphisms and pullback, and — the new capability this
experiment adds — a single-modality observation must be able to recover
the full Observation Bundle O(Q) (Cross-Modal Reconstruction) through the
same categorical machinery.

```
                       [ Observed Target Object Q ]
                     (e.g., "Fate Motif", "Moonlight", "Air on G")
                                    ^
      +-----------------------------+-----------------------------+
      | (m_renders)                 | (m_defines)                 | (m_interprets)
[ Audio Observation ]      [ Score Observation ]        [ Review / Text Observation ]
(.mp3 Waveform)            (Sheet Music .musicxml)      (Critiques / Papers .md)
      |                             |                             |
      v                             v                             v
[ Meaning Mapper ]         [ Meaning Mapper ]           [ Meaning Mapper ]
      |                             |                             |
      v                             v                             v
[ MSR Trajectory ]         [ MSR Trajectory ]           [ MSR Trajectory ]
      +-----------------------------+-----------------------------+
                                    |
                                    v
                       [ Categorical Lift Engine ]
                       (Invariant Signature Lift)
                                    |
                                    v
                    [ HEKB Epistemic Graph / Q ]
                                    |
                                    v
            [ Cross-Modal Reconstruction Engine ]
    (Query 1 Modality --> Recovers Full Observation Bundle O(Q))
```

## II. Multi-Modal Ingestion & Test Matrix

### 1. Multi-Composer / Multi-Work Ingestion Matrix

| Composer | Target Object Q | Modalities (5 per work) |
|---|---|---|
| Beethoven | Symphony No. 5 "Fate" (Q_Sym5) | Audio, Score, Wiki, Critique, Subtitle |
| Beethoven | Piano Sonata No. 14 "Moonlight" (Q_Moonlight) | Audio, Score, Wiki, Critique, Subtitle |
| Beethoven | Symphony No. 9 "Choral" (Q_Sym9) | Audio, Score, Wiki, Critique, Subtitle |
| Mozart | Eine kleine Nachtmusik (Q_K525) | Audio, Score, Wiki, Critique, Subtitle |
| Mozart | Requiem in D minor (Q_K626) | Audio, Score, Wiki, Critique, Subtitle |
| Mozart | Piano Concerto No. 21 (Q_K467) | Audio, Score, Wiki, Critique, Subtitle |
| Bach | Air on the G String (Q_Air) | Audio, Score, Wiki, Critique, Subtitle |
| Bach | Toccata and Fugue in D minor (Q_Toccata) | Audio, Score, Wiki, Critique, Subtitle |
| Bach | WTC Book 1, Prelude No. 1 (Q_WTC1_1) | Audio, Score, Wiki, Critique, Subtitle |

### 2. Target Object Hierarchy (Q_hierarchy)

Each work is indexed as a commutative hierarchy, not a single node:

```
Composer --(m_creates)--> Work --(m_contains)--> Motif --(m_manifests)--> Measure
```

## III. Target Metrics & Acceptance Criteria

1. **Reality Convergence Score (R_convergence)** — potential center mu,
   covariance Sigma, curvature kappa, and Lyapunov exponent lambda from
   different modalities converge into the same attractor region. Target:
   >= 0.95.
2. **Observation Bundle Reconstruction Yield (Y_bundle)** — score
   measure-range, audio timestamp, text paragraph index, and subtitle
   timecode are generated in sync for a query. Target: 100% alignment.
3. **False Convergence Resistance (F_convergence)** — rate at which
   distinct target objects are incorrectly merged into the same S(Q) by
   noise. Target: <= 1.0%.
4. **Cross-Subject Invariant Retrieval Precision (P_invariant)** —
   cross-work queries (e.g. "motif formation by minor third") correctly
   surface structurally-equivalent motifs across composers while
   excluding unrelated works. Target: >= 0.95.
5. **Cross-Modal Reconstruction Accuracy (R_reconstruct)** — given a
   single modality observation, the fraction of ground-truth
   observations recovered: `R_reconstruct = |Recovered| / |Ground Truth|`.
   Target: >= 0.95.
6. **Target Object Hierarchy Resolution** — every resolution level
   (Composer/Work/Motif/Measure) resolves to the correct minimal closure
   S(Q).
7. **Context Economy Ratio (C(Q))** — token-saving ratio of the
   extracted observation bundle relative to all reachable observation
   points. Target: <= 0.15.
8. **Multi-Modal Query Latency (tau_multimodal)** — cross-modal closure
   and bundle retrieval response time over a 45+ observation-point graph.
   Target: < 15ms at p99.

## IV. Cross-Modal Reconstruction Test Suite

- **Test A (Audio-Driven)**: input an audio slice; recover Q, matching
  score measures, Wikipedia paragraph, critique text, and subtitle
  timecode.
- **Test B (Score-Driven)**: input a MusicXML measure range; recover
  audio timestamp, critique, theory analysis, and the abstract invariant
  node.
- **Test C (Critique/Text-Driven)**: input a critique fragment; recover
  the target motif, matching score measures, and audio timecode.
- **Test D (Partial/Minimal Fragment — "the 4-note test")**: input only a
  4-note discrete motif (e.g. G-G-G-Eb) or `Measure 1-2` of a MusicXML
  file; recover the full hierarchy (Composer -> Work -> Movement ->
  Measure), the observation bundle (audio slice, score slice, critique
  paragraph), the invariant signature, cross-subject invariant matches
  in other composers' works, and the proof path.

## V. Phased Execution Matrix

| Phase | Scope | Purpose | Completion Criteria |
|---|---|---|---|
| Phase 1 | 1 composer (Beethoven) x 3 works x 5 modalities | Cross-modality ingest and first convergence onto Q_Fate_Motif; bundle slice confirmation | R_convergence >= 0.95; all 5 modalities synchronized |
| Phase 2 | 3 composers x 3 works (45+ points) | False-convergence resistance across distinct works; cross-composer invariant queries (e.g. "minor third") | F_convergence <= 1.0%; P_invariant >= 0.95 |
| Phase 3 | Cross-Modal Reconstruction Suite (Tests A-D) | Full observation bundle recovery from a single modality; R_reconstruct measurement | R_reconstruct >= 0.95; tau_multimodal < 15ms; C(Q) <= 0.15 |

## VI. Response Payload Schema (Observation Bundle & Proof Path)

```json
{
  "query": {
    "raw_input": "G-G-G-Eb (4-Note Motif Fragment)",
    "input_modality": "ScoreFragment",
    "resolved_target_id": "Beethoven_Sym5_Fate_Motif"
  },
  "target_object": {
    "id": "Beethoven_Sym5_Fate_Motif",
    "canonical_name": "Fate_Motif",
    "hierarchy": {
      "composer": "Ludwig van Beethoven",
      "work": "Symphony No. 5 in C minor, Op. 67",
      "movement": 1,
      "measures": "1-2"
    },
    "invariant_signature": {
      "homotopy_hash": "aef995a28c31f4e...",
      "betti_numbers": [1, 0, 0],
      "potential_params": {
        "mu": [0.12, -0.85, 0.44],
        "sigma_trace": 0.031,
        "curvature_kappa": 1.42,
        "lyapunov_lambda": -8.92
      }
    }
  },
  "observation_bundle": [
    {"modality": "Audio", "source_id": "Beethoven_Sym5_Mvt1_Karajan1977.mp3",
     "slice": {"time_range_s": [0.0, 2.31], "sample_rate": 44100},
     "morphism_type": "acoustically_realizes"},
    {"modality": "Score", "source_id": "Beethoven_Sym5_Mvt1.musicxml",
     "slice": {"measure_range": "1-2", "clef": "treble", "key_signature": "C_minor"},
     "morphism_type": "formally_defines"},
    {"modality": "Critique", "source_id": "Rolland_Beethoven_Analysis_1928.md",
     "slice": {"paragraph_index": 3, "text_excerpt": "..."},
     "morphism_type": "interprets"},
    {"modality": "Wikipedia", "source_id": "Symphony_No_5_(Beethoven).md",
     "slice": {"section": "Motif Analysis", "paragraph_index": 1},
     "morphism_type": "documents"}
  ],
  "cross_subject_invariants": [
    {"target_id": "Bach_WTC1_1_Motif_B", "composer": "Johann Sebastian Bach",
     "work": "Well-Tempered Clavier Book 1, Prelude No. 1",
     "shared_invariant": "Minor_Third_Tension_Release", "signature_similarity": 0.962}
  ],
  "proof_path": [
    "ScoreFragment:G-G-G-Eb",
    "Beethoven_Sym5_Mvt1.musicxml#m=1-2",
    "Beethoven_Sym5_Fate_Motif",
    "Beethoven_Sym5_Mvt1_Karajan1977.mp3#t=0.0-2.31",
    "Rolland_Beethoven_Analysis_1928.md#p=3"
  ],
  "search_metrics": {
    "reality_convergence_score": 0.984,
    "reconstruction_accuracy": 1.0,
    "false_convergence_rate": 0.0,
    "context_economy_ratio": 0.072,
    "execution_time_ms": 4.15
  }
}
```

This example payload is illustrative of the *shape* the response schema
must satisfy; it is not a claim that these numeric values have been
measured (see "Implementation Status" below).

## VII. Revision History

- 2026-08-05: v1.0.0 — initial 3x3 composer/work matrix and cross-modal
  invariant signature identity axioms.
- 2026-08-05: v1.1.0 — added negative controls (F_convergence), Target
  Object Hierarchy (Q_hierarchy), Cross-Subject Invariant Retrieval
  Precision (P_invariant).
- 2026-08-05: v1.2.0 — formalized Observation Bundle Reconstruction
  (Y_bundle) and precise slice metadata in the response schema.
- 2026-08-05: v1.3.0 — added the Cross-Modal Reconstruction Test Suite
  (Tests A-D), including the 4-note minimal-fragment test, formalized
  R_reconstruct, and integrated the full Observation Bundle Recovery
  model.

---

## Implementation Instructions (as supplied with this specification)

Repository status at commissioning: EXP-HEKB001-003 complete and archived
under `experiments/EXP-HEKB00{1,2,3}/`; HEKB Storage, Semantic Closure
Engine, CLE bridge, and MCP reference already exist as the validated
baseline.

**Task**: implement EXP-HEKB004 against the spec above. Do not use vector
or embedding search — retrieval must remain Typed Morphisms / Morphism
Composition / Pullback / Pushout / Semantic Closure only. Reuse
EXP-HEKB003's Semantic Search Engine as-is.

**Repository boundaries**: `src/hekb` (production code) must not be
modified. Only `experiments/`, `experiments/results/`, `CHANGELOG.md`, and
`docs/RFC_ALIGNMENT.md` may be added to or changed. HEKB must remain
storage-ignorant. Graphify does not exist in this workspace; a reference
extractor stands in for it, as in EXP-HEKB001-003.

**Do not fabricate**: no Graphify, no MCP transport, and no homotopy
algorithm exist in this workspace — do not invent them. Only implement
what can be verified with real data; report everything else as an
Architectural Gap, Repository Boundary, or Future Work.

## Implementation Status (added 2026-08-05, post-commissioning)

A repository audit (see `docs/RFC_ALIGNMENT.md`, "EXP-HEKB004") found
**no real audio (`.mp3`/`.wav`), score (`.musicxml`/`.mid`), or subtitle
(`.vtt`) files for any of the 9 target works anywhere in this
environment**, and no composer/work-specific critique or theory text
either. Per this specification's own "do not fabricate" instruction, and
per explicit direction from the requester, implementation is **paused**
at the design stage:

- The Observation Bundle data model, typed-morphism vocabulary, Target
  Object hierarchy, per-modality extractor **interfaces** (Protocols —
  not concrete parsers), the real corpus directory contract, and the
  Cross-Modal Reconstruction Engine (wired to reuse EXP-HEKB003's
  `_semantic_closure`/`_semantic_search` unmodified) are implemented now.
- No corpus ingestion, no Phase 1-3 execution, and no measurement of any
  of the 8 metrics in §III against the real 3x3 matrix has been
  performed. `experiments/results/exp_hekb_004.json` records this
  honestly as `"status": "blocked_on_real_corpus"`.
- Once real files are supplied under the contract documented in
  `experiments/EXP-HEKB004/corpus/README.md`, the experiment is designed
  to be re-run as-is against them, with no changes to the mechanism.

Quality gates before commit: pytest, coverage, ruff check, ruff format
--check, mypy --strict. Do not commit automatically — wait for approval.
