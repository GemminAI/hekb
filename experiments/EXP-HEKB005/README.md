# EXP-HEKB005: Visual Epistemic Target Ingestion, Bounding Crop Recovery & Technique Invariant Validation

## Status

**Implemented against a real corpus.** Unlike EXP-HEKB004 (paused,
design-only), a real 9-work visual+text corpus was fetched, cached, and
ingested; most metrics below are real, measured numbers.

## Purpose

Demonstrate that fragmented visual observations (a high-resolution
master image, a real cropped detail, museum catalog metadata, and
critique/biographical text) of the same real painting converge, through
typed morphisms and pullback/pushout algebra alone, onto the same HEKB
object -- and that recovering that object's full Observation Bundle from
a resolved target id is complete, disambiguated from other works, and
fast.

## Target Repository

`/media/psf/SSD1TB/HEKBv2`.

## Target Specification

EXP-HEKB005 v1.1.0 (full text in `specification.md`).

## Real corpus

`experiments/EXP-HEKB005/corpus/` -- 9 works (Leonardo da Vinci: Mona
Lisa, Virgin of the Rocks, Saint John the Baptist; Johannes Vermeer: Girl
with a Pearl Earring, The Milkmaid, View of Delft; Vincent van Gogh: The
Starry Night, Sunflowers, Bedroom in Arles), fetched once by
`_visual_corpus_fetch.py` from Wikipedia, Wikidata, and Wikimedia Commons
(real images, real structured metadata, real article text), plus real
public-domain critique/biographical text (Vasari, 1911 Encyclopaedia
Britannica, van Gogh's own letters) for 6 of the 9 works. 42 of 45
expected observation points are real and present; see `report.md` for the
honest account of the 3 that are not.

## What exists

- `experiments/_visual_corpus_fetch.py` -- the one-time real fetcher (network calls happen here only).
- `experiments/_visual_observation_bundle.py` -- visual Observation Bundle data model, typed-morphism vocabulary.
- `experiments/_real_visual_extractors.py` -- real parsers reading the cached corpus into `VisualObservation`s.
- `experiments/_visual_reconstruction.py` -- the Visual Observation Bundle Recovery Engine, reusing EXP-HEKB002's `_semantic_closure.compute_closure` unmodified.
- `experiments/exp_hekb_005_visual_reconstruction.py` -- orchestrator: real ingestion, completeness, disambiguation, replay, latency, context economy.

## Reproduction

```bash
cd /media/psf/SSD1TB/HEKBv2
source .venv/bin/activate
cd experiments
# corpus is already cached under EXP-HEKB005/corpus/; re-fetch only if needed:
#   python _visual_corpus_fetch.py   (requires network; not required to replay results)
python exp_hekb_005_visual_reconstruction.py
```

Results land in `experiments/results/exp_hekb_005.json`.

## Quality Gates

```bash
cd /media/psf/SSD1TB/HEKBv2
source .venv/bin/activate
python -m pytest -q
ruff check .
ruff format --check .
python -m mypy .
```

pytest: 29 passed, 91% coverage on `src/hekb` (unchanged) -- ruff check:
clean -- ruff format --check: clean -- mypy --strict (`mypy .`): clean,
41 files.

## Gate dependency: Pillow

Installed into this repository's `.venv` only (`uv pip install --python
.venv/bin/python pillow`), for `experiments/` use, the same pattern
already documented for `msr`/`cle` in `docs/RFC_ALIGNMENT.md`. Not a
declared `pyproject.toml` dependency; `src/hekb` remains
dependency-free.

## Next steps

Real formal `P_invariant` measurement (needs a query benchmark with known
relevant/irrelevant results), real `visual_convergence_score` (needs a
real image-to-meaning measurement model), and real single-fragment ->
target-id resolution (needs a real image-recognition model) are all
recorded as open architectural gaps in `report.md`, not attempted here.
