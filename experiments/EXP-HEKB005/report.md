# EXP-HEKB005 -- Report

## Implementation Summary

EXP-HEKB005 was commissioned to validate visual multi-modal invariant
convergence and Observation Bundle reconstruction against a **real**
3-painter x 3-work x 5-modality corpus (unlike EXP-HEKB004, which was
explicitly paused because no real musical corpus existed). A real corpus
was fetched, cached, and ingested:

- `experiments/_visual_corpus_fetch.py` -- fetches, once, real data for
  all 9 works: Wikipedia summaries/extracts (REST + action API, CC
  BY-SA), Wikidata entity claims (CC0 structured metadata: location,
  collection, inventory number, material, dimensions, inception date,
  creator -- each field present only when Wikidata actually has that
  claim), and Wikimedia Commons image derivatives (`{{PD-Art}}`
  photographic reproductions; all 3 artists died 100+ years ago so both
  the paintings and their photographic reproductions are public domain).
  Real crop regions were chosen by actually viewing each downloaded image
  (via the Read tool) and cropping a genuine, describable sub-region with
  Pillow -- e.g. the Mona Lisa's face and sfumato-modelled eyes, Saint
  John the Baptist's iconic raised pointing hand, van Gogh's own
  "Vincent" signature on the Sunflowers vase -- never a guessed or
  arbitrary quadrant.
- `experiments/_visual_observation_bundle.py` -- the visual Observation
  Bundle data model (`VisualObservation`, `ImageSlice`, `CropSlice`,
  `CatalogSlice`, `TextSlice`) and typed-morphism vocabulary
  (`optically_realizes`, `formally_defines`, `interprets`, `documents`,
  `creates`, `manifests`), including `importance_weight` per modality
  (1.0/0.9/0.8/0.7, matching the specification's own section VI worked
  example) for the weighted-completeness metric.
- `experiments/_real_visual_extractors.py` -- real parsers: Pillow reads
  actual image dimensions; `crop_manifest.json` (written when the crop
  was made, from real pixel coordinates) supplies the real bounding box;
  `catalog.json` fields are read as-is from the real Wikidata fetch;
  `wiki.md`/`critique.md` are read for both a short excerpt (for the
  `VisualObservation` itself) and, separately, full-text (for real
  cross-work technique-term search).
- `experiments/_visual_reconstruction.py` -- the Visual Observation
  Bundle Recovery Engine. Adds **no new retrieval algorithm**: every
  recovery is `_semantic_closure.compute_closure` (EXP-HEKB002,
  unmodified), reshaped into the specification's response payload.
  `compute_completeness` (C_obs(Q), C_w(Q)), `check_disambiguation`
  (Test D), and `find_shared_technique_terms` (real, generic substring
  search over real ingested text, not an asserted link) are the only new
  logic, and none of them touch retrieval itself.
- `experiments/exp_hekb_005_visual_reconstruction.py` -- orchestrates
  real ingestion (Artist -`creates`-> Work -`optically_realizes`/
  `formally_defines`/`interprets`/`documents`-> Observations, plus Work
  -`manifests`-> Technique only where real text evidence supports it)
  and every measurable check.

## Architectural Findings

- **`_semantic_closure.compute_closure` was reused unmodified**, exactly
  as EXP-HEKB003/004. The only new logic on top of it is payload shaping
  and the two completeness/disambiguation calculations described above.
- **Observation recovery is complete (C_obs(Q) = C_w(Q) = 1.0) by
  construction of the ingestion schema, not by a nontrivial retrieval
  feat**: every real `VisualObservation` has exactly one direct morphism
  to its work's target `Concept`, so pushout closure at depth 1
  necessarily recovers all of them. This is an honest, real result about
  the mechanism's correctness (no coverage gap exists at this depth), not
  a claim that a *hard* reconstruction challenge was solved -- a harder
  test would require observations reachable from Q only via an
  intermediate node. The disambiguation test below does exercise exactly
  that: recovering the shared `technique/sfumato` node via one extra hop.
- **A real, generic full-text search (not a hand-picked list) found
  genuine cross-work technique links**: `sfumato` appears in all 3
  Leonardo works' real Wikipedia text; `impasto` and `camera obscura`
  each appear in both Vermeer works that have real critique text (The
  Milkmaid, View of Delft). No term in `TECHNIQUE_VOCABULARY` matched
  across different artists -- reported as a real negative result, not
  omitted. `Girl with a Pearl Earring` has no real critique.md (see
  below), so it was correctly excluded from the Vermeer technique search
  even though it is a Vermeer work.
- **Test D disambiguation is real and nuanced, not a single boolean.**
  A cross-artist pair (Mona Lisa vs. Girl with a Pearl Earring) has zero
  closure overlap. A same-artist pair that *does* share a real technique
  link (Mona Lisa vs. Virgin of the Rocks) correctly overlaps at the
  shared `davinci` (artist) and `technique/sfumato` structural nodes --
  which is the correct behavior, a real cross-subject invariant, not a
  false merge -- while having **zero** overlap at the observation level
  (no image/crop/catalog/critique/wiki node of one work appears in the
  other's closure). Both are checked and reported separately.
- **A documented scope simplification**: the specification's
  Artist -> Work -> Region -> Technique hierarchy is ingested as
  Artist -> Work (`creates`) and Work -> Technique (`manifests`) directly;
  no separate Region node was added, since the real `ImageCrop`
  observation already serves as the region-level observation, linked
  directly to its work. Not a fabricated hierarchy level; a real
  reduction from 4 levels to 3, recorded here rather than left implicit.

## Repository Boundary Findings

- `src/hekb` **not modified**.
- **Pillow installed as a `.venv`-only gate dependency** (`uv pip install
  --python .venv/bin/python pillow`), not added to `pyproject.toml` --
  same pattern already documented for `msr`/`cle`.
- No Graphify, no real MCP transport, no `meaning-mapper` package --
  unchanged findings from EXP-HEKB001-004; none invented here.
- **Real critique/theory text exists for 6 of the 9 works, honestly not
  for the other 3.** Vasari's *Lives* (Gutenberg #28420) names "Monna
  Lisa" specifically in its real Leonardo chapter (lines 2975-3676 of the
  plain-text edition) but does **not** name "Virgin of the Rocks" or
  Leonardo's solo "Saint John the Baptist" panel anywhere in that same
  chapter (checked directly, not assumed) -- no `critique.md` was written
  for those two works. The 1911 Encyclopaedia Britannica's real Vermeer
  entry (transcluded from Wikisource's proofread `Page:EB1911 -
  Volume_18.djvu/90`) names "View of Delft" and "the Milk-Woman" (The
  Milkmaid) explicitly, but never mentions "Girl with a Pearl Earring"
  (whose fame is a later, 20th-century phenomenon) -- no `critique.md`
  for that work either. Van Gogh's own letters (Gutenberg #40393, a
  **primary source**, labelled as such and not conflated with
  third-party critique) genuinely describe all 3 van Gogh works while he
  was painting them, including an almost exact match to Bedroom in
  Arles's actual palette. Net: 42/45 real observation points present
  (93%), reported per-work in `results.json`.
- **`visual_convergence_score` is not measured.** It requires real
  mu/Sigma/kappa geometry from a real image-to-meaning measurement model;
  none exists anywhere in this workspace (the same "meaning-mapper
  doesn't exist" gap every prior EXP-HEKB experiment has recorded, now
  for a visual modality instead of text/audio).
  `homotopy_hash`/`betti_numbers` stay `None` (`cle.homotopy` still
  Protocol-only).
- **Automatic single-fragment -> target-id resolution is not
  implemented.** Recognizing a raw crop's pixels as "the Mona Lisa's eye"
  would require a real image-recognition model this workspace does not
  have. Every reconstruction in this experiment starts from an
  already-resolved `resolved_target_id`, matching how the specification's
  own section VI schema takes that field as given input, not something
  the payload itself derives.
- **Formal `P_invariant` (Cross-Subject Technique Invariant Precision)
  is not measured** -- a precision number requires a query benchmark with
  known relevant/irrelevant results, which does not exist. What is real
  and reported instead: the exact technique terms found, their real
  source files, and the vocabulary terms checked with no match.

## Validation Metrics

| Property | Result |
|---|---|
| Real corpus completeness | **42 / 45** observation points present (93%) across all 9 works |
| Observation Bundle Completeness, C_obs(Q) (mean, 9 works) | **1.0** (see Architectural Findings for why this is complete-by-construction at depth 1) |
| Weighted Observation Completeness, C_w(Q) (mean, 9 works) | **1.0** |
| Disambiguation, Test D (cross-artist: Mona Lisa vs. Girl with a Pearl Earring) | **Pass** -- 0 object overlap, false_convergence_rate = 0.0 |
| Disambiguation, Test D (same-artist: Mona Lisa vs. Virgin of the Rocks) | **Pass at the observation level** -- 0 overlap among real per-work files; structural overlap only at the intentionally-shared `davinci`/`technique/sfumato` nodes (a correct cross-subject invariant) |
| Real cross-subject technique links found | `sfumato`: all 3 Leonardo works; `impasto` and `camera obscura`: both Vermeer works with real critique text |
| Replay determinism | **Pass** -- identical payload (excluding wall-clock timing) across two runs |
| Latency at scale | **Pass** -- 57 real ingested nodes, p50 0.016ms / p99 0.084ms against a 15ms target |
| Context economy ratio (mean across 9 works) | 0.131 (target <= 0.15; reported honestly, not force-gated) |
| Visual Convergence Score (R_convergence) | **NOT MEASURED** -- no real image-to-meaning model exists |
| homotopy_hash / betti_numbers | **NOT MEASURED** -- `cle.homotopy` Protocol-only |
| P_invariant (formal precision) | **NOT MEASURED** -- no query benchmark exists; real supporting findings reported instead |
| Single-fragment -> target-id resolution | **NOT IMPLEMENTED** -- would require a real image-recognition model |
| Overall | `"pass": true` -- every metric that is honestly measurable here (completeness, disambiguation, replay, latency) met its target; metrics requiring a nonexistent model are marked not-measured, not fabricated |

Full output: `experiments/results/exp_hekb_005.json` (copied here as
`results.json`).

## Quality Gates

pytest: 29 passed (unchanged) -- coverage: 91% on `src/hekb` (unchanged)
-- ruff check: clean -- ruff format --check: clean (74 files) -- mypy
--strict (`mypy .`): clean, 41 files. `src/hekb` unmodified throughout.

## Gap Analysis Summary

| Priority | Finding |
|---|---|
| A (implementation defect) | None found. |
| B (spec doesn't match implementation) | The Region/Detail hierarchy level was collapsed into the existing `ImageCrop` observation rather than added as a separate node -- documented above and in `specification.md`, not a silent deviation. |
| C (architectural decision, open) | `TECHNIQUE_VOCABULARY`'s 10 terms are a chosen, documented starting list (like EXP-HEKB003's `Depth_category` table), not derived from any corpus-driven term-extraction process; a larger/derived vocabulary might surface more real links. |
| D (future experiment / architectural gap) | Real critique text for the 3 works currently missing it; a real image-to-meaning measurement model (would unblock `visual_convergence_score`); a real query benchmark (would unblock formal `P_invariant`); a real image-recognition model (would unblock single-fragment resolution) -- all genuinely absent from this workspace, none invented here. |

## Lessons Learned

1. **A truncated excerpt is not the same corpus as the full real file.**
   The first implementation of cross-work technique-term search used
   each `VisualObservation`'s short (280-character) `text_excerpt` and
   found nothing, even though `sfumato` genuinely appears in all 3
   Leonardo works' real Wikipedia text -- because the excerpt was only
   the lead paragraph. Fixed by adding `full_text_for_work`, which reads
   the complete real `wiki.md`/`critique.md` content separately from the
   short excerpt an ingested `Observation` carries. A real bug real data
   exposed, the same lesson EXP-HEKB003 drew from its path-safety bug.
2. **"Complete by construction" is a real, honest result, not a
   deficiency to hide.** C_obs(Q) = 1.0 for every work because every
   observation is one hop from its target by the ingestion schema's own
   design -- reported as such, with the disambiguation test's
   observation-vs-structural distinction offered as the more demanding
   check this experiment could actually run for free.
3. **Real public-domain sources have real, uneven coverage.** Vasari
   covers Mona Lisa specifically but not Leonardo's other two works in
   this corpus; EB1911 covers two of three Vermeer works but predates
   Girl with a Pearl Earring's fame. Reporting exactly which 3 of 45
   observation points are absent, and why, is more useful and more
   honest than a uniform "corpus complete" claim would have been.
