"""EXP-HEKB004's Observation Bundle data model.

Design-stage scaffolding only (see `experiments/EXP-HEKB004/specification.md`,
"Implementation Status"): no real audio, score, or subtitle files exist in
this workspace for any of the 9 target works, so this module defines the
*shape* multi-modal observations must take, not any actual musical
content. Nothing in this file is a claim about a real recording, score, or
critique -- every value a caller constructs here comes from a real file a
caller has read, or it should not be constructed at all.

Follows `hekb.models`' own convention exactly: every value here is a plain,
frozen, `slots=True` dataclass carrying data only, with no behavior. Like
`_functorial_graph_adapter.py`'s `relation_kind` side table, a morphism's
*type* (`Observation.morphism_type`) is a plain string, not a new field
bolted onto `hekb.models.KnowledgeRelation` -- extending that production
model is out of scope for an experiment (EXP-HEKB003's
`docs/RFC_ALIGNMENT.md` already made this same call).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

Modality = Literal["Audio", "Score", "Wiki", "Critique", "Subtitle"]

# Typed-morphism vocabulary from the specification's diagram (section I) and
# response schema (section VI). Hierarchy morphisms walk
# Composer -> Work -> Motif -> Measure; observation morphisms walk a single
# modality observation -> the Observed Target Object Q it is a projection of.
CREATES = "creates"  # Composer -> Work
CONTAINS = "contains"  # Work -> Motif
MANIFESTS = "manifests"  # Motif -> Measure
ACOUSTICALLY_REALIZES = "acoustically_realizes"  # Audio -> Q
FORMALLY_DEFINES = "formally_defines"  # Score -> Q
INTERPRETS = "interprets"  # Critique -> Q
DOCUMENTS = "documents"  # Wiki -> Q
TRANSCRIBES = "transcribes"  # Subtitle -> Q (not named in the spec's worked
# example, which only shows Audio/Score/Critique/Wikipedia; "transcribes" is
# chosen here for the 5th ingestion-matrix modality, Subtitle, following the
# same present-tense-verb naming pattern as the other four.)

HIERARCHY_MORPHISMS = (CREATES, CONTAINS, MANIFESTS)
OBSERVATION_MORPHISMS = (
    ACOUSTICALLY_REALIZES,
    FORMALLY_DEFINES,
    INTERPRETS,
    DOCUMENTS,
    TRANSCRIBES,
)

MODALITY_MORPHISM: dict[Modality, str] = {
    "Audio": ACOUSTICALLY_REALIZES,
    "Score": FORMALLY_DEFINES,
    "Critique": INTERPRETS,
    "Wiki": DOCUMENTS,
    "Subtitle": TRANSCRIBES,
}


@dataclass(frozen=True, slots=True)
class AudioSlice:
    """A real time-range cut of a real audio file. `sample_rate` is only
    known once a real file has actually been read; it is not guessed."""

    time_range_s: tuple[float, float]
    sample_rate: int | None = None


@dataclass(frozen=True, slots=True)
class ScoreSlice:
    """A real measure range of a real MusicXML/MIDI file."""

    measure_range: str
    clef: str | None = None
    key_signature: str | None = None


@dataclass(frozen=True, slots=True)
class TextSlice:
    """A real paragraph/section cut of a real Wiki or Critique Markdown
    file. Used for both the `Wiki` and `Critique` modalities -- both are
    prose text sliced the same way; only the source file and morphism type
    differ."""

    paragraph_index: int
    section: str | None = None
    text_excerpt: str | None = None


@dataclass(frozen=True, slots=True)
class SubtitleSlice:
    """A real timecode cut of a real WebVTT file."""

    time_range_s: tuple[float, float]
    cue_text: str | None = None


ObservationSlice = AudioSlice | ScoreSlice | TextSlice | SubtitleSlice


@dataclass(frozen=True, slots=True)
class Observation:
    """One real, single-modality observation of a Target Object.

    `source_id` MUST name a real file a real extractor actually read (see
    `_multimodal_extractors.py`) -- never a placeholder path standing in
    for a file that does not exist.
    """

    modality: Modality
    source_id: str
    slice: ObservationSlice
    morphism_type: str


@dataclass(frozen=True, slots=True)
class TargetHierarchy:
    """Composer -> Work -> Motif -> Measure, per specification section II.2."""

    composer: str
    work: str
    movement: int | None = None
    measures: str | None = None


@dataclass(frozen=True, slots=True)
class PotentialParams:
    """Geometric parameters of the potential field Phi at the Target
    Object's attractor, as produced by a real MSR `StabilizedTrajectory`
    (see `meaning-space-runtime`'s `msr.abi`) and `msr.lyapunov`. `None`
    until a real trajectory has actually been computed for this target --
    never estimated or interpolated."""

    mu: tuple[float, ...] | None = None
    sigma_trace: float | None = None
    curvature_kappa: float | None = None
    lyapunov_lambda: float | None = None


@dataclass(frozen=True, slots=True)
class InvariantSignature:
    """S(Q) -- the specification's per-target invariant signature.

    `homotopy_hash` and `betti_numbers` require a real homotopy/topology
    algorithm. `cle.homotopy` (in `categorical-lift-engine`) is Protocol-only
    -- no algorithm exists to compute either value, in this workspace or
    any of its dependencies. Both fields stay `None`, honestly, exactly as
    EXP-HEKB002/003 already established for this same gap; a caller MUST
    NOT invent a hash or Betti sequence to fill them.
    """

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
    observations: tuple[Observation, ...]


@dataclass(frozen=True, slots=True)
class CrossSubjectInvariantMatch:
    """One entry of the specification's `cross_subject_invariants` list:
    a different Target Object sharing an invariant with the query's
    target, and how similar its signature is."""

    target_id: str
    composer: str
    work: str
    shared_invariant: str
    signature_similarity: float


__all__ = [
    "ACOUSTICALLY_REALIZES",
    "CONTAINS",
    "CREATES",
    "DOCUMENTS",
    "FORMALLY_DEFINES",
    "HIERARCHY_MORPHISMS",
    "INTERPRETS",
    "MANIFESTS",
    "MODALITY_MORPHISM",
    "OBSERVATION_MORPHISMS",
    "TRANSCRIBES",
    "AudioSlice",
    "CrossSubjectInvariantMatch",
    "InvariantSignature",
    "Modality",
    "Observation",
    "ObservationBundle",
    "ObservationSlice",
    "PotentialParams",
    "ScoreSlice",
    "SubtitleSlice",
    "TargetHierarchy",
    "TargetObject",
    "TextSlice",
]
