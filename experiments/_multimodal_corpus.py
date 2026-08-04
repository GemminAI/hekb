"""EXP-HEKB004's real corpus directory contract and discovery scan.

`WORK_CATALOG` below names the specification's 9 real, public,
already-existing musical works (specification.md section II.1) -- that
catalog is a manifest of what this experiment is looking for, exactly like
`_real_corpus.py`'s `CORPORA`/`MSR_PYTHON_FILES` name the files
EXP-HEKB003 reads. It is not, itself, any audio/score/critique/subtitle
content. `discover_corpus` only ever reports what is *actually* present
under a real directory on disk -- it never invents a file's existence, and
never fabricates content for a file it finds missing.

As of this experiment's design stage (see
`experiments/EXP-HEKB004/specification.md`, "Implementation Status"), a
real filesystem search of this workspace found none of these 45 files;
`discover_corpus()` run against the default corpus root will honestly
report 0/45 present until real files are placed there.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from _observation_bundle import Modality

MODALITY_FILENAMES: dict[Modality, str] = {
    "Audio": "audio.mp3",
    "Score": "score.musicxml",
    "Wiki": "wiki.md",
    "Critique": "critique.md",
    "Subtitle": "subtitle.vtt",
}

CORPUS_ROOT_ENV_VAR = "EXP_HEKB004_CORPUS_ROOT"


@dataclass(frozen=True, slots=True)
class WorkEntry:
    """One row of the specification's 3x3 ingestion matrix (section II.1)."""

    composer: str
    composer_slug: str
    work_slug: str
    canonical_name: str


WORK_CATALOG: tuple[WorkEntry, ...] = (
    WorkEntry(
        "Ludwig van Beethoven", "beethoven", "symphony_no5", "Symphony No. 5 in C minor, Op. 67"
    ),
    WorkEntry(
        "Ludwig van Beethoven",
        "beethoven",
        "moonlight_sonata",
        'Piano Sonata No. 14, Op. 27 No. 2 ("Moonlight")',
    ),
    WorkEntry(
        "Ludwig van Beethoven",
        "beethoven",
        "symphony_no9",
        'Symphony No. 9 in D minor, Op. 125 ("Choral")',
    ),
    WorkEntry(
        "Wolfgang Amadeus Mozart",
        "mozart",
        "eine_kleine_nachtmusik",
        "Eine kleine Nachtmusik, K. 525",
    ),
    WorkEntry("Wolfgang Amadeus Mozart", "mozart", "requiem", "Requiem in D minor, K. 626"),
    WorkEntry(
        "Wolfgang Amadeus Mozart", "mozart", "piano_concerto_no21", "Piano Concerto No. 21, K. 467"
    ),
    WorkEntry(
        "Johann Sebastian Bach",
        "bach",
        "air_on_the_g_string",
        "Air on the G String (Orchestral Suite No. 3, BWV 1068)",
    ),
    WorkEntry(
        "Johann Sebastian Bach",
        "bach",
        "toccata_and_fugue",
        "Toccata and Fugue in D minor, BWV 565",
    ),
    WorkEntry(
        "Johann Sebastian Bach",
        "bach",
        "wtc1_prelude1",
        "Well-Tempered Clavier, Book 1, Prelude No. 1, BWV 846",
    ),
)


@dataclass(frozen=True, slots=True)
class ObservationFileStatus:
    modality: Modality
    expected_path: Path
    present: bool


@dataclass(frozen=True, slots=True)
class WorkCorpusStatus:
    work: WorkEntry
    files: tuple[ObservationFileStatus, ...]

    @property
    def complete(self) -> bool:
        return all(f.present for f in self.files)

    @property
    def present_count(self) -> int:
        return sum(1 for f in self.files if f.present)

    def as_dict(self) -> dict[str, Any]:
        return {
            "composer": self.work.composer,
            "work": self.work.canonical_name,
            "work_slug": self.work.work_slug,
            "complete": self.complete,
            "present_count": self.present_count,
            "expected_count": len(self.files),
            "files": [
                {
                    "modality": f.modality,
                    "expected_path": str(f.expected_path),
                    "present": f.present,
                }
                for f in self.files
            ],
        }


@dataclass(frozen=True, slots=True)
class CorpusManifest:
    root: Path
    works: tuple[WorkCorpusStatus, ...]

    @property
    def total_expected(self) -> int:
        return sum(len(w.files) for w in self.works)

    @property
    def total_present(self) -> int:
        return sum(w.present_count for w in self.works)

    @property
    def is_empty(self) -> bool:
        return self.total_present == 0

    def as_dict(self) -> dict[str, Any]:
        return {
            "root": str(self.root),
            "total_expected": self.total_expected,
            "total_present": self.total_present,
            "works": [w.as_dict() for w in self.works],
        }


def default_corpus_root() -> Path:
    return Path(__file__).with_name("EXP-HEKB004") / "corpus"


def resolve_corpus_root() -> Path:
    """The real directory to search: `EXP_HEKB004_CORPUS_ROOT` if set (so a
    caller can point this at a real corpus once one exists, without editing
    this module), else the default path documented in
    `experiments/EXP-HEKB004/corpus/README.md`."""
    override = os.environ.get(CORPUS_ROOT_ENV_VAR)
    return Path(override) if override else default_corpus_root()


def expected_path(root: Path, work: WorkEntry, modality: Modality) -> Path:
    return root / work.composer_slug / work.work_slug / MODALITY_FILENAMES[modality]


def discover_corpus(root: Path | None = None) -> CorpusManifest:
    """Scan a real directory and report, per work and modality, whether the
    expected real file is actually present. Never raises on a missing
    directory or missing files -- "nothing found" is a legitimate, honestly
    reported outcome, not an error."""
    resolved_root = root if root is not None else resolve_corpus_root()
    works = tuple(
        WorkCorpusStatus(
            work=entry,
            files=tuple(
                ObservationFileStatus(
                    modality=modality,
                    expected_path=(path := expected_path(resolved_root, entry, modality)),
                    present=path.is_file(),
                )
                for modality in MODALITY_FILENAMES
            ),
        )
        for entry in WORK_CATALOG
    )
    return CorpusManifest(root=resolved_root, works=works)


__all__ = [
    "CORPUS_ROOT_ENV_VAR",
    "MODALITY_FILENAMES",
    "WORK_CATALOG",
    "CorpusManifest",
    "ObservationFileStatus",
    "WorkCorpusStatus",
    "WorkEntry",
    "default_corpus_root",
    "discover_corpus",
    "expected_path",
    "resolve_corpus_root",
]
