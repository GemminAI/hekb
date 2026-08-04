# EXP-HEKB004 real corpus directory contract

This directory is the real corpus root `experiments/_multimodal_corpus.py`
scans (override with the `EXP_HEKB004_CORPUS_ROOT` environment variable to
point at a different real location instead of editing that module).

It is currently empty: no real audio, score, critique, or subtitle files
for any of the 9 target works exist anywhere in this workspace (see
`../specification.md`, "Implementation Status"). `discover_corpus()`
reports this honestly as 0/45 observation points present; nothing in
`experiments/exp_hekb_004_multimodal_convergence.py` fabricates a
replacement.

## Expected layout

Once real files are available, place them under:

```
corpus/<composer_slug>/<work_slug>/audio.mp3
corpus/<composer_slug>/<work_slug>/score.musicxml
corpus/<composer_slug>/<work_slug>/wiki.md
corpus/<composer_slug>/<work_slug>/critique.md
corpus/<composer_slug>/<work_slug>/subtitle.vtt
```

`<composer_slug>`/`<work_slug>` pairs (see
`_multimodal_corpus.WORK_CATALOG` for the canonical names each maps to):

| composer_slug | work_slug |
|---|---|
| beethoven | symphony_no5 |
| beethoven | moonlight_sonata |
| beethoven | symphony_no9 |
| mozart | eine_kleine_nachtmusik |
| mozart | requiem |
| mozart | piano_concerto_no21 |
| bach | air_on_the_g_string |
| bach | toccata_and_fugue |
| bach | wtc1_prelude1 |

A work does not need all 5 files to be partially usable -- `discover_corpus()`
reports presence per file, not just per work -- but the specification's
Phase 1-3 metrics (`R_convergence`, `F_convergence`, `P_invariant`,
`R_reconstruct`, `Y_bundle`, `C(Q)`, `tau_multimodal`) require the full
5-modality bundle for at least the Beethoven works (Phase 1) to be
meaningfully measured, and all 9 works (Phase 2-3) to be measured as
specified.

## What happens once files are here

`experiments/exp_hekb_004_multimodal_convergence.py` re-run against a
non-empty corpus is designed to ingest the present files via the
per-modality extractors described in `_multimodal_extractors.py`, lift
them through the same real `msr`/`cle` pipeline EXP-HEKB002/003 already
validate (`_msr_cle_pipeline.py`, `_cle_hekb_adapter.py`), and measure the
specification's 8 metrics against what was actually ingested -- no change
to the mechanism itself is anticipated, only wiring real extractor bodies
in place of the `NotImplementedError` reference stubs in
`_multimodal_extractors.py`.
