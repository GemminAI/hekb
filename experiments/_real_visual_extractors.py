"""EXP-HEKB005's real visual/text extractors.

Unlike EXP-HEKB004's `_multimodal_extractors.py` (Protocol boundaries
only, no bodies -- no real files existed to implement against), every
function here is a real, working parser, because
`_visual_corpus_fetch.py` already populated
`experiments/EXP-HEKB005/corpus/` with real files. Each function reads
exactly the real file named, and constructs a `VisualObservation` only
from what that file actually contains -- a modality whose file is absent
for a given work (e.g. no `critique.md`) is simply omitted, never
synthesized.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from PIL import Image

from _visual_corpus_fetch import CORPUS_ROOT, VisualWorkEntry, work_dir
from _visual_observation_bundle import (
    DEFAULT_IMPORTANCE_WEIGHT,
    DOCUMENTS,
    FORMALLY_DEFINES,
    INTERPRETS,
    OPTICALLY_REALIZES,
    CatalogSlice,
    CropSlice,
    ImageSlice,
    TextSlice,
    VisualObservation,
)

MODALITY_FILES = {
    "HighResImage": ("image.jpg", "image.png"),
    "ImageCrop": ("crop.png",),
    "MuseumCatalog": ("catalog.json",),
    "Critique": ("critique.md",),
    "Wiki": ("wiki.md",),
}


@dataclass(frozen=True, slots=True)
class ModalityFileStatus:
    modality: str
    path: Path
    present: bool


@dataclass(frozen=True, slots=True)
class WorkCorpusStatus:
    work: VisualWorkEntry
    files: tuple[ModalityFileStatus, ...]

    @property
    def present_count(self) -> int:
        return sum(1 for f in self.files if f.present)

    def as_dict(self) -> dict[str, Any]:
        return {
            "artist": self.work.artist,
            "work": self.work.canonical_name,
            "work_slug": self.work.work_slug,
            "present_count": self.present_count,
            "expected_count": len(self.files),
            "files": [
                {"modality": f.modality, "path": str(f.path), "present": f.present}
                for f in self.files
            ],
        }


def _find_present_file(directory: Path, candidates: tuple[str, ...]) -> Path | None:
    for name in candidates:
        candidate = directory / name
        if candidate.is_file():
            return candidate
    return None


def discover_visual_corpus(catalog: tuple[VisualWorkEntry, ...]) -> tuple[WorkCorpusStatus, ...]:
    """Real filesystem scan of `experiments/EXP-HEKB005/corpus/` -- reports
    exactly what is present, mirroring `_multimodal_corpus.discover_corpus`'s
    "never invent a file's existence" contract."""
    statuses = []
    for work in catalog:
        directory = work_dir(work)
        files = tuple(
            ModalityFileStatus(
                modality=modality,
                path=directory / candidates[0],
                present=_find_present_file(directory, candidates) is not None,
            )
            for modality, candidates in MODALITY_FILES.items()
        )
        statuses.append(WorkCorpusStatus(work=work, files=files))
    return tuple(statuses)


def extract_high_res_image(work: VisualWorkEntry) -> VisualObservation | None:
    directory = work_dir(work)
    image_path = _find_present_file(directory, MODALITY_FILES["HighResImage"])
    source_path = directory / "image_source.json"
    if image_path is None:
        return None
    with Image.open(image_path) as img:
        resolution = img.size
    source_url = None
    license_short_name = None
    if source_path.is_file():
        source = json.loads(source_path.read_text())
        source_url = source.get("downloaded_derivative_url")
        license_short_name = source.get("license_short_name")
    return VisualObservation(
        modality="HighResImage",
        source_id=f"{work.artist_slug}/{work.work_slug}/{image_path.name}",
        slice=ImageSlice(
            resolution_px=resolution, source_url=source_url, license_short_name=license_short_name
        ),
        morphism_type=OPTICALLY_REALIZES,
        importance_weight=DEFAULT_IMPORTANCE_WEIGHT["HighResImage"],
    )


def extract_image_crop(work: VisualWorkEntry) -> VisualObservation | None:
    directory = work_dir(work)
    crop_path = _find_present_file(directory, MODALITY_FILES["ImageCrop"])
    manifest_path = directory / "crop_manifest.json"
    if crop_path is None or not manifest_path.is_file():
        return None
    manifest = json.loads(manifest_path.read_text())
    normalized = manifest["bounding_box_normalized_ymin_xmin_ymax_xmax"]
    return VisualObservation(
        modality="ImageCrop",
        source_id=f"{work.artist_slug}/{work.work_slug}/{crop_path.name}",
        slice=CropSlice(
            bounding_box_normalized=tuple(normalized),
            pixel_bbox_ltrb=tuple(manifest["pixel_bbox_ltrb"]),
            rationale=manifest["rationale"],
        ),
        morphism_type=OPTICALLY_REALIZES,
        importance_weight=DEFAULT_IMPORTANCE_WEIGHT["ImageCrop"],
    )


def extract_museum_catalog(work: VisualWorkEntry) -> VisualObservation | None:
    directory = work_dir(work)
    catalog_path = _find_present_file(directory, MODALITY_FILES["MuseumCatalog"])
    if catalog_path is None:
        return None
    catalog = json.loads(catalog_path.read_text())
    fields = {k: (v if isinstance(v, str) else json.dumps(v)) for k, v in catalog["fields"].items()}
    return VisualObservation(
        modality="MuseumCatalog",
        source_id=f"{work.artist_slug}/{work.work_slug}/{catalog_path.name}",
        slice=CatalogSlice(fields=fields, wikidata_qid=catalog["wikidata_qid"]),
        morphism_type=FORMALLY_DEFINES,
        importance_weight=DEFAULT_IMPORTANCE_WEIGHT["MuseumCatalog"],
    )


_HEADER_SOURCE_RE = re.compile(r"^Source: (.+)$", re.MULTILINE)


def _extract_text_observation(
    work: VisualWorkEntry, modality: str, candidates: tuple[str, ...], morphism_type: str
) -> VisualObservation | None:
    directory = work_dir(work)
    path = _find_present_file(directory, candidates)
    if path is None:
        return None
    text = path.read_text()
    # `critique.md` files use a `---` divider between the citation header
    # and the real quoted excerpt; `wiki.md` files don't, so fall back to
    # skipping only the header lines (#-title, Source:/Retrieved: block).
    body = text.split("\n---\n", 1)[-1] if "\n---\n" in text else text
    paragraphs = [p.strip() for p in body.split("\n\n") if p.strip()]
    body_paragraphs = [
        p
        for p in paragraphs
        if not p.startswith("#") and not p.startswith("Source:") and not p.startswith("Retrieved:")
    ]
    excerpt = body_paragraphs[0] if body_paragraphs else None
    return VisualObservation(
        modality=modality,  # type: ignore[arg-type]
        source_id=f"{work.artist_slug}/{work.work_slug}/{path.name}",
        slice=TextSlice(
            paragraph_index=0,
            text_excerpt=(excerpt[:280] if excerpt else None),
        ),
        morphism_type=morphism_type,
        importance_weight=DEFAULT_IMPORTANCE_WEIGHT[modality],  # type: ignore[index]
    )


def extract_critique(work: VisualWorkEntry) -> VisualObservation | None:
    return _extract_text_observation(work, "Critique", MODALITY_FILES["Critique"], INTERPRETS)


def full_text_for_work(work: VisualWorkEntry) -> str:
    """The complete real text of `wiki.md` + `critique.md` for `work`
    (whichever are present) -- unlike the short `TextSlice.text_excerpt`
    an ingested `VisualObservation` carries, this is the full real file
    content, for real full-text search (see
    `_visual_reconstruction.find_shared_technique_terms`), not a truncated
    280-character quote."""
    directory = work_dir(work)
    parts = []
    for candidates in (MODALITY_FILES["Wiki"], MODALITY_FILES["Critique"]):
        path = _find_present_file(directory, candidates)
        if path is not None:
            parts.append(path.read_text())
    return "\n".join(parts)


def extract_wiki(work: VisualWorkEntry) -> VisualObservation | None:
    return _extract_text_observation(work, "Wiki", MODALITY_FILES["Wiki"], DOCUMENTS)


def extract_observations_for_work(work: VisualWorkEntry) -> tuple[VisualObservation, ...]:
    """Every real observation actually present for `work` -- up to 5
    (HighResImage, ImageCrop, MuseumCatalog, Critique, Wiki), fewer if a
    real source file is genuinely absent (see `discover_visual_corpus`)."""
    extracted = (
        extract_high_res_image(work),
        extract_image_crop(work),
        extract_museum_catalog(work),
        extract_critique(work),
        extract_wiki(work),
    )
    return tuple(obs for obs in extracted if obs is not None)


__all__ = [
    "CORPUS_ROOT",
    "MODALITY_FILES",
    "ModalityFileStatus",
    "WorkCorpusStatus",
    "discover_visual_corpus",
    "extract_critique",
    "extract_high_res_image",
    "extract_image_crop",
    "extract_museum_catalog",
    "extract_observations_for_work",
    "extract_wiki",
    "full_text_for_work",
]
