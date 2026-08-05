"""EXP-HEKB006 v2.1.0 Phase 1: real Human-vs-Human Ground Truth construction.

The specification's Phase 1 asks for a Ground Truth closure built from
"multiple independent expert sources" -- art historians, catalog
raisonnes, monographs -- before any AI observer is considered. This
workspace has no live human-expert panel to query, but EXP-HEKB005's real
corpus (`experiments/EXP-HEKB005/corpus/`, fetched once by
`_visual_corpus_fetch.py`) already contains three genuinely
independently-authored real human text/data channels for the same real
target objects:

- **Critique** (`critique.md`) -- a named human critic's own real words
  (Vasari, the 1911 Encyclopaedia Britannica, or Vincent van Gogh's own
  letters, depending on the work) interpreting the work. Present for 6 of
  9 works.
- **Wiki** (`wiki.md`) -- Wikipedia's editorial community's real,
  independently-written documentation of the same work. Present for all
  9 works.
- **MuseumCatalog** (`catalog.json`) -- Wikidata's real, independently
  curated structured metadata (location, collection, material, dates) for
  the same work. Present for all 9 works.

Treating each of these three real, independently-produced channels as one
"Human Observer" of the same real target object is not fabrication: each
one is a real file, written by a real, distinct human source, already
ingested by EXP-HEKB005 -- this module only re-partitions that already-real
ingestion by channel (instead of EXP-HEKB005's single combined category)
so each channel's closure can stand alone and be compared against the
others via `_reality_consensus.py`. No new corpus is fetched, no text is
generated, and `_semantic_closure.compute_closure` (EXP-HEKB002) is reused
unmodified, exactly as every real-corpus experiment in this series already
does.

Each channel's cross-work technique links (`MANIFESTS` edges to a shared
`technique/<term>` node) are computed from **that channel's own real text
alone** via `_visual_reconstruction.find_shared_technique_terms`, reused
unmodified -- a Critique-channel observer's closure never borrows evidence
found only in that work's Wiki text, and vice versa. `MuseumCatalog` is
structured data, not prose, so no technique-term search applies to it: a
`MuseumCatalog` observer's closure is structural (artist/work/observation
nodes) only, honestly, not padded with technique links it has no textual
basis for.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from _real_visual_extractors import extract_critique, extract_museum_catalog, extract_wiki
from _reality_consensus import ObserverClosure
from _semantic_closure import SemanticClosure, compute_closure
from _visual_corpus_fetch import WORK_CATALOG, VisualWorkEntry, work_dir
from _visual_observation_bundle import CREATES, MANIFESTS, VisualObservation
from _visual_reconstruction import find_shared_technique_terms
from hekb.category import KnowledgeCategory
from hekb.models import Concept, KnowledgeRelation

#: Specification's "Human Expert Panel" analogue -- three real,
#: independently-authored channels already present in EXP-HEKB005's real
#: corpus. `filename` is `None` for channels with no prose text to search
#: for cross-work technique terms.
HumanChannel = str
HUMAN_CHANNELS: tuple[HumanChannel, ...] = ("Human_Critique", "Human_Wiki", "Human_MuseumCatalog")

_EXTRACTOR: dict[HumanChannel, Callable[[VisualWorkEntry], VisualObservation | None]] = {
    "Human_Critique": extract_critique,
    "Human_Wiki": extract_wiki,
    "Human_MuseumCatalog": extract_museum_catalog,
}
_TEXT_FILENAME: dict[HumanChannel, str | None] = {
    "Human_Critique": "critique.md",
    "Human_Wiki": "wiki.md",
    "Human_MuseumCatalog": None,
}


def work_target_id(work: VisualWorkEntry) -> str:
    return f"{work.artist_slug}/{work.work_slug}"


@dataclass(frozen=True, slots=True)
class HumanChannelResult:
    """One real channel's independent ingestion across every work that
    actually has that channel's file present -- `closures_by_target` has
    fewer than 9 entries whenever a work's real corpus is missing that
    channel's file (e.g. no `critique.md` for 3 of 9 works), never a
    synthesized stand-in."""

    channel: HumanChannel
    closures_by_target: dict[str, SemanticClosure]
    technique_links: dict[str, tuple[str, ...]]
    works_present: tuple[str, ...]
    works_absent: tuple[str, ...]


def build_human_channel(channel: HumanChannel) -> HumanChannelResult:
    """Ingest exactly one real human channel across the real
    EXP-HEKB005 corpus: artist->work structural scaffolding (every real
    observer would independently reconstruct the same artist attribution
    from the same real Wikidata/Wikipedia record), this channel's own real
    per-work observation edge, and cross-work technique links found in
    this channel's own real text alone (empty for `MuseumCatalog`, which
    has no prose to search)."""
    extractor = _EXTRACTOR[channel]
    text_filename = _TEXT_FILENAME[channel]

    category = KnowledgeCategory()
    relation_kind: dict[str, str] = {}
    object_category: dict[str, str] = {}
    artists_ingested: set[str] = set()
    target_ids_present: list[str] = []
    target_ids_absent: list[str] = []
    work_texts: dict[str, str] = {}

    for work in WORK_CATALOG:
        target_id = work_target_id(work)
        observation = extractor(work)
        if observation is None:
            target_ids_absent.append(target_id)
            continue

        artist_id = work.artist_slug
        if artist_id not in artists_ingested:
            category.add_object(Concept(id=artist_id, elements=frozenset({artist_id})))
            object_category[artist_id] = "Artist"
            artists_ingested.add(artist_id)

        category.add_object(Concept(id=target_id, elements=frozenset({target_id})))
        object_category[target_id] = "TargetObject"
        creates = KnowledgeRelation(
            id=f"{artist_id}_creates_{target_id}",
            source=artist_id,
            target=target_id,
            mapping={artist_id: target_id},
        )
        category.add_morphism(creates)
        relation_kind[creates.id] = CREATES

        obs_id = observation.source_id
        category.add_object(Concept(id=obs_id, elements=frozenset({obs_id})))
        object_category[obs_id] = observation.modality
        obs_relation = KnowledgeRelation(
            id=f"{obs_id}_{observation.morphism_type}_{target_id}",
            source=obs_id,
            target=target_id,
            mapping={obs_id: target_id},
        )
        category.add_morphism(obs_relation)
        relation_kind[obs_relation.id] = observation.morphism_type

        target_ids_present.append(target_id)
        if text_filename is not None:
            path = work_dir(work) / text_filename
            if path.is_file():
                work_texts[target_id] = path.read_text()

    technique_links = find_shared_technique_terms(work_texts) if text_filename is not None else {}
    for term, work_ids in technique_links.items():
        technique_id = f"technique/{term.replace(' ', '_')}"
        if technique_id not in category.objects:
            category.add_object(Concept(id=technique_id, elements=frozenset({technique_id})))
            object_category[technique_id] = "Technique"
        for target_id in work_ids:
            relation_id = f"{target_id}_manifests_{technique_id}"
            if relation_id in category.morphisms:
                continue
            relation = KnowledgeRelation(
                id=relation_id,
                source=target_id,
                target=technique_id,
                mapping={target_id: technique_id},
            )
            category.add_morphism(relation)
            relation_kind[relation_id] = MANIFESTS

    closures_by_target = {
        target_id: compute_closure(category, relation_kind, object_category, target_id)
        for target_id in target_ids_present
    }

    return HumanChannelResult(
        channel=channel,
        closures_by_target=closures_by_target,
        technique_links=technique_links,
        works_present=tuple(sorted(target_ids_present)),
        works_absent=tuple(sorted(target_ids_absent)),
    )


def build_all_human_channels() -> tuple[HumanChannelResult, ...]:
    return tuple(build_human_channel(channel) for channel in HUMAN_CHANNELS)


def observers_by_work(
    channels: tuple[HumanChannelResult, ...],
) -> dict[str, tuple[ObserverClosure, ...]]:
    """Regroup per-channel results by target work: for each real work,
    every real human channel that actually has a file for it becomes one
    `ObserverClosure` -- 2 observers for works with only Wiki+MuseumCatalog,
    3 for works that additionally have a real critique.md."""
    by_work: dict[str, list[ObserverClosure]] = {}
    for result in channels:
        for target_id, closure in result.closures_by_target.items():
            by_work.setdefault(target_id, []).append(
                ObserverClosure(observer=result.channel, closure=closure)
            )
    return {target_id: tuple(observers) for target_id, observers in sorted(by_work.items())}


__all__ = [
    "HUMAN_CHANNELS",
    "HumanChannel",
    "HumanChannelResult",
    "build_all_human_channels",
    "build_human_channel",
    "observers_by_work",
    "work_target_id",
]
