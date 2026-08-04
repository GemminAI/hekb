# EXP-HEKB005: Visual Epistemic Target Ingestion, Bounding Crop Recovery & Technique Invariant Validation

- **Project**: SensOS Core & Enterprise Project / Multi-Modal Epistemic Integration Series
- **Date**: 2026-08-05
- **Version**: 1.1.0 (Observation Bundle Completeness & Weighted Recovery Expansion)
- **Status**: Proposed / Active Specification -- implemented against a real corpus (see "Implementation Status" below)
- **Target Components**: `meaning-mapper`, `msr`, `cle-core`, `HEKB Storage Engine`, `Semantic Closure Engine`, `Semantic Search Engine`, `HEKB MCP Service`
- **Upstream Sources**:
  1. Heterogeneous visual observation streams: high-res images (`.png`/`.jpg`), partial crop bounding regions (`.json`/`.png`), museum catalog metadata (`.json`), art history papers & critiques (`.md`), Wikipedia/provenance docs (`.md`)
  2. Visual test corpus: 3 painters x 3 masterworks (9 Observed Target Objects Q, 45+ observation points)
- **Downstream Target**: Multi-Modal Visual Context Injection, Cross-Subject Technique Search Engine

## I. Executive Summary & Rationale

EXP-HEKB005 extends EXP-HEKB004's multi-modal convergence framework
(time-varying audio/music) to static 2D visual art, where geometric/
topological ground truth is most precisely definable because no
performance-time variation exists. High-resolution master images, partial
crops (bounding regions of eyes, hands, signatures, skylines), museum
catalog data, academic technique papers, and critique text are all
different observations of the same underlying Observed Target Object
Q_painting.

The experiment ingests a "3 painters x 3 works x 5 modalities (45+
observation points)" visual corpus and validates that a partial image
crop recovers the corresponding full image, museum description, technique
papers, and historical context (Observation Bundle Recovery), quantified
via Observation Bundle Completeness (C_obs(Q)) and Weighted Observation
Completeness (C_w(Q)).

```
                         [ Observed Target Object Q ]
                     (e.g., "Mona Lisa", "The Starry Night")
                                    ^
      +-----------------------------+-----------------------------+
      | (m_renders)                 | (m_defines)                 | (m_interprets)
[ Visual Observation ]       [ Crop / Region Slice ]      [ Art History / Review ]
(High-Res Image .png)        (Bounding Box Crop .png)     (Critiques / Papers .md)
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
            [ Visual Observation Bundle Recovery Engine ]
     (Query Crop Fragment --> Recovers Full Observation Bundle O(Q))
```

## II. Visual Multi-Modal Ingestion & Test Matrix

### 1. Multi-Painter / Multi-Work Ingestion Matrix

| Painter | Target Object Q | Modalities (5 per work) |
|---|---|---|
| Leonardo da Vinci | Mona Lisa | High-Res Image, Crop Slice, Catalog, Critique, Wiki |
| Leonardo da Vinci | Virgin of the Rocks (Louvre version) | High-Res Image, Crop Slice, Catalog, Critique, Wiki |
| Leonardo da Vinci | Saint John the Baptist | High-Res Image, Crop Slice, Catalog, Critique, Wiki |
| Johannes Vermeer | Girl with a Pearl Earring | High-Res Image, Crop Slice, Catalog, Critique, Wiki |
| Johannes Vermeer | The Milkmaid | High-Res Image, Crop Slice, Catalog, Critique, Wiki |
| Johannes Vermeer | View of Delft | High-Res Image, Crop Slice, Catalog, Critique, Wiki |
| Vincent van Gogh | The Starry Night | High-Res Image, Crop Slice, Catalog, Critique, Wiki |
| Vincent van Gogh | Sunflowers (F454) | High-Res Image, Crop Slice, Catalog, Critique, Wiki |
| Vincent van Gogh | Bedroom in Arles | High-Res Image, Crop Slice, Catalog, Critique, Wiki |

This experiment's implementation used the painter/work list supplied with
the implementation instructions (Leonardo da Vinci, Johannes Vermeer,
Vincent van Gogh), which differs from an earlier illustrative example in
an initial draft of this specification (which named Claude Monet in place
of Vermeer) -- the implementation instructions are authoritative.

### 2. Target Object Hierarchy (Q_visual_hierarchy)

```
Artist --(m_creates)--> Work --(m_contains)--> Region/Detail --(m_manifests)--> Technique/Invariance
```

This implementation ingests the Artist -> Work level (`creates`) and a
Work -> Technique level (`manifests`, only where real text evidence
supports a specific technique term -- see "Implementation Status")
directly; an explicit intermediate Region/Detail node was not added as a
separate hierarchy level (the `ImageCrop` observation already serves as
the region-level observation of a work, linked directly to it) -- a
documented scope simplification, not a fabricated hierarchy level.

## III. Target Metrics & Acceptance Criteria

1. **Visual Convergence Score (R_convergence)** -- Target: >= 0.95.
2. **Visual Observation Bundle Reconstruction Yield (Y_bundle)** -- Target: 100% alignment.
3. **False Convergence Resistance (F_convergence)** -- Target: <= 1.0%.
4. **Cross-Subject Technique Invariant Precision (P_invariant)** -- Target: >= 0.95.
5. **Observation Bundle Completeness (C_obs(Q))** -- `|Recovered| / |Ground Truth|`. Target: >= 0.95.
6. **Weighted Observation Completeness (C_w(Q))** -- `sum(w_i * I_i) / sum(w_i)`. Target: >= 0.95.
7. **Target Object Hierarchy Resolution** -- every resolution level resolves to the correct minimal closure S(Q).
8. **Visual Context Economy Ratio (C(Q))** -- Target: <= 0.15.
9. **Visual Retrieval Latency (tau_visual)** -- Target: < 15ms at p99.

## IV. Visual Reconstruction & Fragment Test Suite

- **Test A (Image Crop Fragment / "Eye & Hand" test)**: partial crop -> target node, full image, bbox, museum text, technique node.
- **Test B (Critique/Text-Driven)**: critique fragment -> technique node, related works, corresponding crops.
- **Test C (Bounding Region Metadata)**: normalized bbox spec -> region interpretation, historical critique, invariant signature.
- **Test D (Disambiguation)**: visually similar but distinct works (e.g. two different portraits' eyes) must resolve to strictly separate Q nodes, 0% false-merge.

## V. Phased Execution Matrix

| Phase | Scope | Purpose | Completion Criteria |
|---|---|---|---|
| Phase 1 | 1 painter (Leonardo) x 3 works x 5 modalities | Crop ingestion and first convergence onto Q_MonaLisa | R_convergence >= 0.95, all 5 modalities synchronized |
| Phase 2 | 3 painters x 3 works (45+ points) | False-convergence resistance, cross-technique queries | F_convergence <= 1.0%, P_invariant >= 0.95 |
| Phase 3 | Visual Reconstruction Suite (Tests A-D) | Full bundle recovery from a single crop; C_obs(Q)/C_w(Q) | C_obs(Q) >= 0.95, C_w(Q) >= 0.95, tau_visual < 15ms, C(Q) <= 0.15 |

## VI. Response Payload Schema (Visual Bounding Slice & Proof Path)

See the specification's worked JSON example (target_object with
`invariant_signature`, `observation_bundle` entries each carrying
`modality`/`source_id`/`slice`/`morphism_type`/`importance_weight`,
`cross_subject_invariants`, `proof_path`, `search_metrics`). This example
is illustrative of the response *shape*; it is not a claim that these
exact numeric values have been measured (see "Implementation Status").

## VII. Revision History

- 2026-08-05: v1.0.0 -- initial 3x3 visual test matrix, fragment crop reconstruction tests, technique invariant pullback queries, response schema.
- 2026-08-05: v1.1.0 -- formalized Observation Bundle Completeness (C_obs(Q)) and Weighted Observation Completeness (C_w(Q)), updated section III/VI.

---

## Implementation Instructions (as supplied with this specification)

Same engineering policy as EXP-HEKB001-004. Reuse real production code
(Semantic Closure, HEKB storage, Observation Bundle mechanism, MM/MSR/CLE
interfaces, ConceptStore/adapters) unchanged. Do not invent Graphify, an
MCP server, Meaning Mapper, CLE functionality, or topology algorithms; do
not fabricate measurements, benchmark numbers, or corpus statistics.

**Unlike EXP-HEKB004, this experiment MUST use REAL publicly available
visual corpus data** -- 3 painters x 3 works (Leonardo da Vinci: Mona
Lisa, Virgin of the Rocks, Saint John the Baptist; Johannes Vermeer: Girl
with a Pearl Earring, The Milkmaid, View of Delft; Vincent van Gogh:
Starry Night, Sunflowers, Bedroom in Arles), each modality real wherever
available. Measure only what is actually measurable; mark `BLOCKED`/`NOT
MEASURED` rather than fabricate. Create everything under `experiments/`;
leave `src/hekb` unchanged. Do not commit automatically -- report
Architectural Findings, Repository Boundary Findings, Validation Metrics,
Quality Gates, and Changed Files, and wait for approval.

## Implementation Status (added 2026-08-05, post-commissioning)

Unlike EXP-HEKB004, a real corpus was actually fetched and ingested:

- `experiments/_visual_corpus_fetch.py` fetched, once, real data for all
  9 works from Wikipedia (REST + action API, CC BY-SA text), Wikidata
  (CC0 structured metadata), and Wikimedia Commons (`{{PD-Art}}`
  photographic reproductions of public-domain paintings -- all 3 artists
  died 100+ years ago). Real crop regions were chosen by actually viewing
  each downloaded image and cropping a genuine, describable sub-region
  with Pillow (installed as a `.venv`-only gate dependency, not added to
  `pyproject.toml` -- see `docs/RFC_ALIGNMENT.md`).
- Real public-domain critique/theory text was found and used for 6 of the
  9 works (Vasari's *Lives* for Mona Lisa; the 1911 Encyclopaedia
  Britannica's Vermeer entry for The Milkmaid and View of Delft, both
  named explicitly in that real source; Vincent van Gogh's own letters,
  a primary source, for all 3 van Gogh works, each genuinely describing
  that specific picture). For the remaining 3 works (Virgin of the Rocks,
  Saint John the Baptist, Girl with a Pearl Earring), no real
  public-domain critique text naming that specific work could be found --
  no `critique.md` was written for these, and the gap is reported
  honestly rather than papered over. Net real corpus completeness: 42/45
  observation points (93%).
- `experiments/_real_visual_extractors.py`, `_visual_observation_bundle.py`,
  `_visual_reconstruction.py`, and `exp_hekb_005_visual_reconstruction.py`
  ingest this real corpus into a real `hekb.category.KnowledgeCategory`
  and measure Observation Bundle Completeness, Weighted Completeness,
  disambiguation (Test D), replay determinism, latency at scale, and
  context economy -- all real, computed numbers.
- `visual_convergence_score` (R_convergence), `homotopy_hash`/
  `betti_numbers`, and formal `P_invariant` (precision requires a query
  benchmark that does not exist) are **not measured**, honestly, per the
  same discipline EXP-HEKB002-004 already established for equivalent
  gaps. Automatic single-fragment -> target-id *resolution* (recognizing
  a raw crop as "the Mona Lisa's eye" from pixels alone) is also not
  implemented -- it would require a real image-recognition model this
  workspace does not have.

See `report.md` for full findings and measured metrics.

Quality gates before commit: pytest, coverage, ruff check, ruff format
--check, mypy --strict. Do not commit automatically -- wait for approval.
