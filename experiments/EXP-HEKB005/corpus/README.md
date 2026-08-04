# EXP-HEKB005 real corpus

Every file under this directory is real: real Wikimedia Commons image
derivatives, real Wikidata structured metadata, real Wikipedia article
text, real public-domain critique/letter excerpts, and real Pillow crops
of the real downloaded images at coordinates chosen by actually viewing
each one. Fetched once by `../../_visual_corpus_fetch.py`
(`python _visual_corpus_fetch.py` from `experiments/`, requires network;
not required to replay `exp_hekb_005_visual_reconstruction.py`'s results
against this already-cached corpus).

## Layout

```
corpus/<artist_slug>/<work_slug>/image.jpg          # real Commons derivative
corpus/<artist_slug>/<work_slug>/image_source.json  # real provenance (Commons file, license, retrieval time)
corpus/<artist_slug>/<work_slug>/crop.png           # real Pillow crop of image.jpg
corpus/<artist_slug>/<work_slug>/crop_manifest.json # real pixel + normalized bbox, rationale
corpus/<artist_slug>/<work_slug>/catalog.json       # real Wikidata fields (only those Wikidata actually has)
corpus/<artist_slug>/<work_slug>/wiki.md            # real Wikipedia extract (CC BY-SA)
corpus/<artist_slug>/<work_slug>/critique.md        # real public-domain critique/letter excerpt -- ABSENT for 3 works, see below
```

## Real completeness: 42 / 45 observation points

`critique.md` is intentionally **absent** for:

- `davinci/virgin_of_the_rocks` -- no passage naming this work found in
  Vasari's real Leonardo chapter (Gutenberg #28420, lines 2975-3676).
- `davinci/saint_john_the_baptist` -- same source, same chapter, same
  real search, no match found.
- `vermeer/girl_with_a_pearl_earring` -- the real 1911 Encyclopaedia
  Britannica Vermeer entry (Wikisource `Page:EB1911 -
  Volume_18.djvu/90`) never mentions this painting; its fame is a later,
  20th-century phenomenon.

No file was fabricated to fill these gaps. See `../report.md`,
"Repository Boundary Findings", for the full account, including which
real sources *were* found and used for the other 6 works.
