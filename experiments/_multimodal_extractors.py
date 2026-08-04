"""EXP-HEKB004's per-modality extractor boundaries.

Extractor *interfaces* only -- the "extractor boundaries" the requester
asked be designed first, deliberately stopping short of a concrete
implementation. Every modality's real extraction depends on a real file
that does not exist anywhere in this workspace (see
`experiments/EXP-HEKB004/specification.md`, "Implementation Status"), so
writing a concrete parser now would mean either (a) never exercising it
against a real file, or (b) fabricating one to test against -- both are
exactly what the requester asked this experiment to avoid. Each `Protocol`
below is the real contract a concrete extractor must satisfy once a real
file is supplied; `_reference_stub` documents, per modality, what a real
implementation is expected to do and the real library/approach it would
use, without producing any output.

This mirrors how `_graphify_reference.py`/`_mcp_reference.py` are labeled
reference stand-ins, not the real thing -- except here there is not even a
fixture, because a fixture would be exactly the kind of synthetic
observation data the requester asked not to be created.
"""

from __future__ import annotations

from pathlib import Path
from typing import Protocol, runtime_checkable

from _multimodal_corpus import WorkEntry
from _observation_bundle import Modality, Observation


@runtime_checkable
class ModalityExtractor(Protocol):
    """The shape every real per-modality extractor must satisfy: read one
    real file for one real work, and produce one real `Observation`
    grounded in what that file actually contains."""

    def extract(self, path: Path, work: WorkEntry) -> Observation: ...


# What a real implementation of each extractor is expected to do, and the
# real library/approach it would use -- recorded here so the boundary is
# concrete, not vague, even though no body is written yet.
REFERENCE_APPROACH: dict[Modality, str] = {
    "Audio": (
        "Decode the real .mp3/.wav via a real audio library (e.g. "
        "soundfile/librosa), locate the target motif's real onset via "
        "onset detection or a supplied real timecode, and emit an "
        "AudioSlice(time_range_s=..., sample_rate=<the file's real rate>)."
    ),
    "Score": (
        "Parse the real MusicXML via a real parser (e.g. music21 or "
        "direct ElementTree over the MusicXML schema), locate the real "
        "measure range, and emit a ScoreSlice(measure_range=..., "
        "clef=..., key_signature=...) read from that file's real header."
    ),
    "Wiki": (
        "Read the real Markdown/Wikipedia-export file, split on real "
        "paragraph boundaries, and emit a TextSlice(paragraph_index=..., "
        "section=..., text_excerpt=<the real paragraph text>)."
    ),
    "Critique": (
        "Same approach as Wiki -- real Markdown, real paragraph split -- "
        "over a real critique/paper file instead of a Wikipedia export."
    ),
    "Subtitle": (
        "Parse the real WebVTT file's real cue blocks (timestamp + text), "
        "matching against a supplied real time range or search text, and "
        "emit a SubtitleSlice(time_range_s=..., cue_text=<the real cue>)."
    ),
}


def reference_extractor(modality: Modality, path: Path, work: WorkEntry) -> Observation:
    """Always raises: no concrete extractor is implemented for any
    modality yet, because no real file exists to implement one against.
    Calling this documents exactly what is missing and why, rather than
    returning a fabricated `Observation`."""
    raise NotImplementedError(
        f"no real {modality} file exists for {work.canonical_name!r} in this "
        f"workspace (expected at {path}); a real extractor is not implemented "
        f"until one does. Expected approach once real data is available: "
        f"{REFERENCE_APPROACH[modality]}"
    )


__all__ = ["REFERENCE_APPROACH", "ModalityExtractor", "reference_extractor"]
