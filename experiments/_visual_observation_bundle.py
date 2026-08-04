"""EXP-HEKB005's visual Observation Bundle data model.

The visual analogue of EXP-HEKB004's `_observation_bundle.py`, following
its exact conventions (plain, frozen, `slots=True` dataclasses; morphism
*type* as a string carried in a side table, not a new field on
`hekb.models.KnowledgeRelation`). Unlike EXP-HEKB004, real files exist
behind every value constructed from this module -- see
`_real_visual_extractors.py`, which reads them from
`experiments/EXP-HEKB005/corpus/`.

`importance_weight` on `VisualObservation` is the specification's `w_i`
(section III.6, Weighted Observation Completeness `C_w(Q)`) -- a
domain-importance weight assigned per modality, not computed, matching
the specification's own worked example (`"importance_weight": 1.0`, 0.9,
0.8, 0.7 in section VI's response schema for
HighResImage/MuseumCatalog/Critique/ArtHistoryPaper respectively).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

Modality = Literal["HighResImage", "ImageCrop", "MuseumCatalog", "Critique", "Wiki"]

# Typed-morphism vocabulary from the specification's diagram (section I)
# and response schema (section VI). Hierarchy morphisms walk
# Artist -> Work -> Region/Detail -> Technique; observation morphisms walk
# a single modality observation -> the Observed Target Object Q it is a
# projection of.
CREATES = "creates"  # Artist -> Work
CONTAINS = "contains"  # Work -> Region/Detail
MANIFESTS = "manifests"  # Region/Detail -> Technique/Invariance
OPTICALLY_REALIZES = "optically_realizes"  # HighResImage / ImageCrop -> Q
FORMALLY_DEFINES = "formally_defines"  # MuseumCatalog -> Q
INTERPRETS = "interprets"  # Critique -> Q
DOCUMENTS = "documents"  # Wiki -> Q

HIERARCHY_MORPHISMS = (CREATES, CONTAINS, MANIFESTS)
OBSERVATION_MORPHISMS = (OPTICALLY_REALIZES, FORMALLY_DEFINES, INTERPRETS, DOCUMENTS)

MODALITY_MORPHISM: dict[Modality, str] = {
    "HighResImage": OPTICALLY_REALIZES,
    "ImageCrop": OPTICALLY_REALIZES,
    "MuseumCatalog": FORMALLY_DEFINES,
    "Critique": INTERPRETS,
    "Wiki": DOCUMENTS,
}

# Domain-importance weights per modality, matching the specification's own
# section VI worked example (HighResImage 1.0, MuseumCatalog 0.9,
# Critique 0.8, Wiki/ArtHistoryPaper 0.7). A chosen, documented ordinal
# scale -- not derived from any measurement -- exactly like EXP-HEKB003's
# `Depth_category` table was a chosen, documented ordinal, not a learned
# signal. ImageCrop shares HighResImage's weight: both are direct optical
# observations of the same real work.
DEFAULT_IMPORTANCE_WEIGHT: dict[Modality, float] = {
    "HighResImage": 1.0,
    "ImageCrop": 1.0,
    "MuseumCatalog": 0.9,
    "Critique": 0.8,
    "Wiki": 0.7,
}


@dataclass(frozen=True, slots=True)
class ImageSlice:
    """A real image file's real dimensions. `source_url`/`license` trace
    back to `image_source.json`, written by `_visual_corpus_fetch.py` from
    a real Commons API response -- never guessed."""

    resolution_px: tuple[int, int]
    source_url: str | None = None
    license_short_name: str | None = None


@dataclass(frozen=True, slots=True)
class CropSlice:
    """A real Pillow crop of a real image, at a bounding box chosen by
    actually viewing the real image (see `crop_manifest.json`, written by
    `_visual_corpus_fetch.write_crop`) -- never a guessed or generated
    region."""

    bounding_box_normalized: tuple[float, float, float, float]  # ymin, xmin, ymax, xmax
    pixel_bbox_ltrb: tuple[int, int, int, int]
    rationale: str


@dataclass(frozen=True, slots=True)
class CatalogSlice:
    """The real fields read from `catalog.json` (itself sourced from a
    real Wikidata entity), following `hekb.models.Concept.invariants`'s
    own convention of a plain `dict` field inside a frozen dataclass.
    `fields` carries every real field Wikidata actually had for this work
    (location, collection, inventory_number, material_used, height_cm,
    width_cm, inception, creator) -- a field Wikidata has no claim for is
    simply absent from the dict, never invented. `wikidata_qid` makes the
    exact real entity traceable."""

    fields: dict[str, str]
    wikidata_qid: str


@dataclass(frozen=True, slots=True)
class TextSlice:
    """A real excerpt of a real Wiki or Critique Markdown file. Used for
    both modalities -- both are prose text, sliced the same way; only the
    source file and morphism type differ."""

    paragraph_index: int
    section: str | None = None
    text_excerpt: str | None = None


VisualObservationSlice = ImageSlice | CropSlice | CatalogSlice | TextSlice


@dataclass(frozen=True, slots=True)
class VisualObservation:
    """One real, single-modality observation of a Target Object.

    `source_id` MUST name a real file a real extractor actually read (see
    `_real_visual_extractors.py`) -- never a placeholder path standing in
    for a file that does not exist. `importance_weight` is `w_i` from the
    specification's `C_w(Q)` formula (section III.6).
    """

    modality: Modality
    source_id: str
    slice: VisualObservationSlice
    morphism_type: str
    importance_weight: float


@dataclass(frozen=True, slots=True)
class TargetHierarchy:
    """Artist -> Work -> Region -> Technique, per specification section II.2."""

    artist: str
    work: str
    region: str | None = None
    period: str | None = None


@dataclass(frozen=True, slots=True)
class PotentialParams:
    """Geometric parameters of the potential field Phi at the Target
    Object's attractor, as would be produced by a real MSR
    `StabilizedTrajectory` derived from a real image-to-meaning
    measurement. `None` until such a trajectory has actually been
    computed for this target -- never estimated or interpolated. No
    image-to-meaning-measurement model exists anywhere in this workspace
    (the same gap `meaning-mapper` is for every other EXP-HEKB
    experiment), so every real ingestion in this experiment leaves this
    `None`; see `_msr_cle_pipeline`-style mechanism-only demonstrations in
    `_visual_reconstruction.py` for what *is* shown to be wired, clearly
    labelled as not a real visual-convergence measurement."""

    mu: tuple[float, ...] | None = None
    sigma_trace: float | None = None
    curvature_kappa: float | None = None
    lyapunov_lambda: float | None = None


@dataclass(frozen=True, slots=True)
class InvariantSignature:
    """S(Q) -- the specification's per-target invariant signature.
    `homotopy_hash`/`betti_numbers` require a real homotopy/topology
    algorithm; `cle.homotopy` is still Protocol-only. Both stay `None`,
    exactly as EXP-HEKB002-004 already established for this same gap."""

    homotopy_hash: str | None = None
    betti_numbers: tuple[int, ...] | None = None
    potential_params: PotentialParams | None = None


@dataclass(frozen=True, slots=True)
class TargetObject:
    """Q -- the Observed Target Object every modality's observations are a
    projection of. `id` MUST be the id of a real `hekb.models.Concept`
    already admitted to a `hekb.category.KnowledgeCategory`."""

    id: str
    canonical_name: str
    hierarchy: TargetHierarchy
    invariant_signature: InvariantSignature | None = None


@dataclass(frozen=True, slots=True)
class ObservationBundle:
    """O(Q) -- every real observation gathered for one Target Object."""

    target: TargetObject
    observations: tuple[VisualObservation, ...]


@dataclass(frozen=True, slots=True)
class CrossSubjectInvariantMatch:
    """One entry of the specification's `cross_subject_invariants` list: a
    different Target Object sharing a real, textually-evidenced technique
    invariant with the query's target. `evidence_source_id` MUST name the
    real corpus file (e.g. `"davinci/mona_lisa/critique.md"`) where the
    shared term was actually found -- this dataclass carries no field for
    an unsupported/asserted-only link; see `_visual_reconstruction.py`'s
    `find_shared_technique_terms` for how the link is verified before one
    of these is constructed."""

    target_id: str
    artist: str
    work: str
    shared_invariant: str
    evidence_source_id: str


__all__ = [
    "CONTAINS",
    "CREATES",
    "DEFAULT_IMPORTANCE_WEIGHT",
    "DOCUMENTS",
    "FORMALLY_DEFINES",
    "HIERARCHY_MORPHISMS",
    "INTERPRETS",
    "MANIFESTS",
    "MODALITY_MORPHISM",
    "OBSERVATION_MORPHISMS",
    "OPTICALLY_REALIZES",
    "CatalogSlice",
    "CropSlice",
    "CrossSubjectInvariantMatch",
    "ImageSlice",
    "InvariantSignature",
    "Modality",
    "ObservationBundle",
    "PotentialParams",
    "TargetHierarchy",
    "TargetObject",
    "TextSlice",
    "VisualObservation",
    "VisualObservationSlice",
]
