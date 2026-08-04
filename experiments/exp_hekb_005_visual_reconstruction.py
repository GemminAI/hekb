"""EXP-HEKB005 -- Visual Epistemic Target Ingestion, Bounding Crop
Recovery & Technique Invariant Validation.

Builds on EXP-HEKB001 (persistence), EXP-HEKB002 (closed-loop validation),
EXP-HEKB003 (real-world semantic search), and EXP-HEKB004 (multi-modal
design, blocked on a real corpus) without redesigning any of them.
Unlike EXP-HEKB004, this experiment ingests a REAL corpus --
`experiments/EXP-HEKB005/corpus/`, built once by `_visual_corpus_fetch.py`
from real Wikipedia, Wikidata, and Wikimedia Commons data, plus real
public-domain critique text (Vasari, EB1911, van Gogh's own letters) --
and measures what that real ingestion actually supports.

Retrieval is exactly `_semantic_closure.compute_closure` (EXP-HEKB002),
reused unmodified via `_visual_reconstruction.reconstruct` -- no vector or
embedding search anywhere.

**Not measured, honestly**: `visual_convergence_score` (needs a real
image-to-meaning measurement model; none exists anywhere in this
workspace) and `homotopy_hash`/`betti_numbers` (`cle.homotopy` is still
Protocol-only). Single-modality-fragment -> target-id *resolution* (e.g.
recognizing a crop as "the Mona Lisa's eye" from pixels alone) is also not
implemented -- it would require a real image-recognition model this
workspace does not have; every reconstruction below starts from an
already-resolved `resolved_target_id`, exactly as the specification's own
response schema takes `resolved_target_id` as a given field, not
something section VI's payload itself computes.
"""

from __future__ import annotations

import json
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from _concept_store import FileConceptStore
from _file_backend import FileProjectionBackend
from _real_visual_extractors import (
    discover_visual_corpus,
    extract_observations_for_work,
    full_text_for_work,
)
from _visual_corpus_fetch import WORK_CATALOG, VisualWorkEntry
from _visual_observation_bundle import (
    CREATES,
    MANIFESTS,
    CrossSubjectInvariantMatch,
    TargetHierarchy,
    TargetObject,
    VisualObservation,
)
from _visual_reconstruction import (
    ReconstructionQuery,
    check_disambiguation,
    find_shared_technique_terms,
    reconstruct,
    reconstruction_payload,
)
from hekb.category import KnowledgeCategory
from hekb.models import Concept, KnowledgeRelation
from hekb.runtime import HEKBCoreRuntime

STORE_ROOT = Path(__file__).with_name("_hekb_store") / "exp_hekb_005"
RELATION_STORE = STORE_ROOT / "relations"
CONCEPT_STORE = STORE_ROOT / "concepts"

LATENCY_TARGET_MS = 15.0
LATENCY_SAMPLE_COUNT = 100
COMPLETENESS_TARGET = 0.95


def _fresh_dir(path: Path) -> Path:
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True)
    return path


def work_target_id(work: VisualWorkEntry) -> str:
    return f"{work.artist_slug}/{work.work_slug}"


def artist_id(work: VisualWorkEntry) -> str:
    return work.artist_slug


@dataclass
class IngestResult:
    category: KnowledgeCategory
    relation_kind: dict[str, str]
    object_category: dict[str, str]
    observations_by_id: dict[str, VisualObservation]
    ground_truth_by_work: dict[str, tuple[VisualObservation, ...]]
    work_texts: dict[str, str]
    technique_links: dict[str, tuple[str, ...]]
    structural_ids: set[str]
    corpus_manifest: list[dict[str, Any]]


def run_stage1_corpus_discovery() -> list[dict[str, Any]]:
    statuses = discover_visual_corpus(WORK_CATALOG)
    return [s.as_dict() for s in statuses]


def ingest_real_corpus() -> IngestResult:
    concept_root = _fresh_dir(CONCEPT_STORE)
    relation_root = _fresh_dir(RELATION_STORE)
    concept_backend = FileConceptStore(concept_root)
    relation_backend = FileProjectionBackend(relation_root)
    runtime = HEKBCoreRuntime(relation_backend)

    relation_kind: dict[str, str] = {}
    object_category: dict[str, str] = {}
    observations_by_id: dict[str, VisualObservation] = {}
    ground_truth_by_work: dict[str, tuple[VisualObservation, ...]] = {}
    work_texts: dict[str, str] = {}
    structural_ids: set[str] = set()

    artists_ingested: set[str] = set()

    for work in WORK_CATALOG:
        a_id = artist_id(work)
        if a_id not in artists_ingested:
            artist_concept = Concept(id=a_id, elements=frozenset({a_id}))
            runtime.ingest_object(artist_concept)
            concept_backend.write(artist_concept)
            object_category[a_id] = "Artist"
            structural_ids.add(a_id)
            artists_ingested.add(a_id)

        target_id = work_target_id(work)
        target_concept = Concept(id=target_id, elements=frozenset({target_id}))
        runtime.ingest_object(target_concept)
        concept_backend.write(target_concept)
        object_category[target_id] = "TargetObject"
        structural_ids.add(target_id)

        creates_relation = KnowledgeRelation(
            id=f"{a_id}_{CREATES}_{target_id}",
            source=a_id,
            target=target_id,
            mapping={a_id: target_id},
        )
        runtime.ingest_morphism(creates_relation)
        relation_kind[creates_relation.id] = CREATES

        observations = extract_observations_for_work(work)
        ground_truth_by_work[target_id] = observations
        for obs in observations:
            obs_id = obs.source_id
            obs_concept = Concept(id=obs_id, elements=frozenset({obs_id}))
            runtime.ingest_object(obs_concept)
            concept_backend.write(obs_concept)
            object_category[obs_id] = obs.modality
            relation = KnowledgeRelation(
                id=f"{obs_id}_{obs.morphism_type}_{target_id}",
                source=obs_id,
                target=target_id,
                mapping={obs_id: target_id},
            )
            runtime.ingest_morphism(relation)
            relation_kind[relation.id] = obs.morphism_type
            observations_by_id[obs_id] = obs
        # Full real wiki.md + critique.md text (not the short excerpt an
        # ingested Observation carries) -- see
        # `find_shared_technique_terms`, which needs real full-text
        # search, not a 280-character quote.
        work_texts[target_id] = full_text_for_work(work)

    # Real cross-subject technique links: only for terms actually found in
    # >= 2 works' real ingested text (see
    # `_visual_reconstruction.find_shared_technique_terms`).
    technique_links = find_shared_technique_terms(work_texts)
    for term, work_ids in technique_links.items():
        technique_id = f"technique/{term.replace(' ', '_')}"
        technique_concept = Concept(id=technique_id, elements=frozenset({technique_id}))
        runtime.ingest_object(technique_concept)
        concept_backend.write(technique_concept)
        object_category[technique_id] = "Technique"
        structural_ids.add(technique_id)
        for target_id in work_ids:
            manifests_relation = KnowledgeRelation(
                id=f"{target_id}_{MANIFESTS}_{technique_id}",
                source=target_id,
                target=technique_id,
                mapping={target_id: technique_id},
            )
            runtime.ingest_morphism(manifests_relation)
            relation_kind[manifests_relation.id] = MANIFESTS

    corpus_manifest = [s.as_dict() for s in discover_visual_corpus(WORK_CATALOG)]

    return IngestResult(
        category=runtime.category,
        relation_kind=relation_kind,
        object_category=object_category,
        observations_by_id=observations_by_id,
        ground_truth_by_work=ground_truth_by_work,
        work_texts=work_texts,
        technique_links=technique_links,
        structural_ids=structural_ids,
        corpus_manifest=corpus_manifest,
    )


def _target_object_for(work: VisualWorkEntry) -> TargetObject:
    return TargetObject(
        id=work_target_id(work),
        canonical_name=work.canonical_name,
        hierarchy=TargetHierarchy(artist=work.artist, work=work.canonical_name),
    )


def run_completeness_checks(ingest: IngestResult) -> dict[str, Any]:
    """C_obs(Q) and C_w(Q) (specification.md section III.5/III.6) for
    every real ingested work: given the work's own target id as an
    already-resolved query, how much of its real ground-truth observation
    set does the real pushout closure recover."""
    per_work: dict[str, Any] = {}
    obs_values = []
    weighted_values = []
    for work in WORK_CATALOG:
        target_id = work_target_id(work)
        cross_subject = tuple(
            CrossSubjectInvariantMatch(
                target_id=other_id,
                artist=next(w.artist for w in WORK_CATALOG if work_target_id(w) == other_id),
                work=next(w.canonical_name for w in WORK_CATALOG if work_target_id(w) == other_id),
                shared_invariant=term,
                evidence_source_id=next(
                    obs.source_id
                    for obs in ingest.ground_truth_by_work[target_id]
                    if obs.modality in ("Wiki", "Critique")
                ),
            )
            for term, work_ids in ingest.technique_links.items()
            if target_id in work_ids
            for other_id in work_ids
            if other_id != target_id
        )
        result = reconstruct(
            category=ingest.category,
            relation_kind=ingest.relation_kind,
            object_category=ingest.object_category,
            query=ReconstructionQuery(
                raw_input=f"resolved-target:{target_id}",
                input_modality="PreResolved",
                resolved_target_id=target_id,
            ),
            target=_target_object_for(work),
            observations_by_id=ingest.observations_by_id,
            ground_truth_observations=ingest.ground_truth_by_work[target_id],
            cross_subject_invariants=cross_subject,
        )
        payload = reconstruction_payload(result)
        per_work[target_id] = {
            "observation_completeness": result.completeness.observation_completeness,
            "weighted_observation_completeness": (
                result.completeness.weighted_observation_completeness
            ),
            "recovered_count": result.completeness.recovered_count,
            "ground_truth_count": result.completeness.ground_truth_count,
            "cross_subject_invariants": payload["cross_subject_invariants"],
            "proof_path": payload["proof_path"],
        }
        obs_values.append(result.completeness.observation_completeness)
        weighted_values.append(result.completeness.weighted_observation_completeness)

    mean_obs = sum(obs_values) / len(obs_values)
    mean_weighted = sum(weighted_values) / len(weighted_values)
    return {
        "per_work": per_work,
        "mean_observation_completeness": mean_obs,
        "mean_weighted_observation_completeness": mean_weighted,
        "target": COMPLETENESS_TARGET,
        "target_met": bool(
            mean_obs >= COMPLETENESS_TARGET and mean_weighted >= COMPLETENESS_TARGET
        ),
    }


def run_disambiguation_checks(ingest: IngestResult) -> dict[str, Any]:
    """Test D: cross-artist and same-artist-different-work disambiguation,
    both computed from the real ingested category."""
    mona_lisa = work_target_id(WORK_CATALOG[0])
    pearl_earring = work_target_id(WORK_CATALOG[3])
    virgin_of_rocks = work_target_id(WORK_CATALOG[1])

    cross_artist = check_disambiguation(
        ingest.category, ingest.relation_kind, ingest.object_category, mona_lisa, pearl_earring
    )
    same_artist = check_disambiguation(
        ingest.category, ingest.relation_kind, ingest.object_category, mona_lisa, virgin_of_rocks
    )
    # A same-artist pair sharing a real technique link (see
    # `technique_links`) is EXPECTED to overlap at that shared, structural
    # `technique/...` node -- that is a correct cross-subject invariant,
    # not false convergence. Only overlap at real per-work observation
    # nodes (image/crop/catalog/critique/wiki files) counts as an actual
    # false merge.
    observation_overlap = [
        oid for oid in same_artist["overlap_object_ids"] if oid not in ingest.structural_ids
    ]
    return {
        "cross_artist_pair": cross_artist,
        "same_artist_pair": {
            **same_artist,
            "structural_overlap_ids": [
                oid for oid in same_artist["overlap_object_ids"] if oid in ingest.structural_ids
            ],
            "observation_level_overlap_ids": observation_overlap,
            "observation_level_disambiguated": len(observation_overlap) == 0,
        },
        "pass": bool(cross_artist["disambiguated"] and len(observation_overlap) == 0),
    }


def run_replay_determinism(ingest: IngestResult) -> dict[str, Any]:
    target_id = work_target_id(WORK_CATALOG[0])

    def _normalized() -> dict[str, Any]:
        result = reconstruct(
            category=ingest.category,
            relation_kind=ingest.relation_kind,
            object_category=ingest.object_category,
            query=ReconstructionQuery(
                raw_input=f"resolved-target:{target_id}",
                input_modality="PreResolved",
                resolved_target_id=target_id,
            ),
            target=_target_object_for(WORK_CATALOG[0]),
            observations_by_id=ingest.observations_by_id,
            ground_truth_observations=ingest.ground_truth_by_work[target_id],
        )
        payload = reconstruction_payload(result)
        payload["search_metrics"].pop("execution_time_ms")
        return payload

    first = _normalized()
    second = _normalized()
    return {"deterministic": first == second, "pass": bool(first == second)}


def run_latency_at_scale(ingest: IngestResult) -> dict[str, Any]:
    target_id = work_target_id(WORK_CATALOG[0])
    latencies_ms: list[float] = []
    for _ in range(LATENCY_SAMPLE_COUNT):
        result = reconstruct(
            category=ingest.category,
            relation_kind=ingest.relation_kind,
            object_category=ingest.object_category,
            query=ReconstructionQuery(
                raw_input=f"resolved-target:{target_id}",
                input_modality="PreResolved",
                resolved_target_id=target_id,
            ),
            target=_target_object_for(WORK_CATALOG[0]),
            observations_by_id=ingest.observations_by_id,
            ground_truth_observations=ingest.ground_truth_by_work[target_id],
        )
        latencies_ms.append(result.search_metrics.execution_time_ms)
    latencies_ms.sort()
    p50 = latencies_ms[len(latencies_ms) // 2]
    p99 = latencies_ms[int(len(latencies_ms) * 0.99)]
    return {
        "sample_count": LATENCY_SAMPLE_COUNT,
        "node_count": len(ingest.category.objects),
        "latency_p50_ms": p50,
        "latency_p99_ms": p99,
        "latency_target_ms": LATENCY_TARGET_MS,
        "pass": bool(p99 < LATENCY_TARGET_MS),
    }


def run_context_economy(ingest: IngestResult) -> dict[str, Any]:
    per_work = {}
    for work in WORK_CATALOG:
        target_id = work_target_id(work)
        result = reconstruct(
            category=ingest.category,
            relation_kind=ingest.relation_kind,
            object_category=ingest.object_category,
            query=ReconstructionQuery(
                raw_input=f"resolved-target:{target_id}",
                input_modality="PreResolved",
                resolved_target_id=target_id,
            ),
            target=_target_object_for(work),
            observations_by_id=ingest.observations_by_id,
            ground_truth_observations=ingest.ground_truth_by_work[target_id],
        )
        per_work[target_id] = result.search_metrics.context_economy_ratio
    values = [v for v in per_work.values() if v is not None]
    mean_ratio = sum(values) / len(values) if values else None
    return {
        "per_work": per_work,
        "mean_context_economy_ratio": mean_ratio,
        "target": 0.15,
        "note": (
            "reported honestly, not force-gated on the 0.15 target -- a "
            "real, query-dependent number on this real corpus's actual scale"
        ),
    }


def run_technique_invariant_findings(ingest: IngestResult) -> dict[str, Any]:
    """Cross-Subject Technique Invariant Precision (P_invariant,
    specification.md section III.4) is NOT formally measured here: doing
    so honestly requires a query benchmark with known relevant/irrelevant
    results, which does not exist. What IS real and reported: every
    technique term this experiment actually found co-occurring across >=2
    works' real ingested text, with the exact real source file as
    evidence for each match -- and, explicitly, which candidate terms
    were checked but did NOT cross-match (so the vocabulary and the
    negative results are visible too, not just the hits)."""
    checked_but_not_shared = sorted(_all_checked_terms_not_in(ingest.technique_links))
    return {
        "p_invariant_formally_measured": False,
        "p_invariant_reason": (
            "requires a query benchmark with known relevant/irrelevant "
            "results, which does not exist -- reporting a precision "
            "number without one would be fabrication"
        ),
        "real_shared_technique_terms_found": {
            term: list(work_ids) for term, work_ids in ingest.technique_links.items()
        },
        "vocabulary_terms_checked_with_no_cross_work_match": checked_but_not_shared,
    }


def _all_checked_terms_not_in(technique_links: dict[str, tuple[str, ...]]) -> list[str]:
    from _visual_reconstruction import TECHNIQUE_VOCABULARY

    return [term for term in TECHNIQUE_VOCABULARY if term not in technique_links]


def run() -> dict[str, Any]:
    uncaught_exception: str | None = None
    try:
        corpus = run_stage1_corpus_discovery()
        ingest = ingest_real_corpus()
        completeness = run_completeness_checks(ingest)
        disambiguation = run_disambiguation_checks(ingest)
        replay = run_replay_determinism(ingest)
        latency = run_latency_at_scale(ingest)
        context_economy = run_context_economy(ingest)
        technique = run_technique_invariant_findings(ingest)
        total_expected = sum(w["expected_count"] for w in corpus)
        total_present = sum(w["present_count"] for w in corpus)
    except Exception as exc:
        uncaught_exception = f"{type(exc).__name__}: {exc}"
        corpus = []
        completeness = disambiguation = replay = latency = context_economy = technique = {
            "pass": False
        }
        total_expected = total_present = 0

    result: dict[str, Any] = {
        "experiment": "EXP-HEKB005",
        "scope": (
            "Real visual + text corpus (9 works: 3 Leonardo da Vinci, 3 "
            "Johannes Vermeer, 3 Vincent van Gogh) fetched once from "
            "Wikipedia, Wikidata, Wikimedia Commons, and public-domain "
            "critique sources (Vasari, EB1911, van Gogh's own letters) by "
            "_visual_corpus_fetch.py, cached under "
            "experiments/EXP-HEKB005/corpus/, and ingested here via real "
            "hekb.category.KnowledgeCategory + "
            "_semantic_closure.compute_closure (EXP-HEKB002, unmodified). "
            "No vector/embedding search anywhere. src/hekb not modified. "
            "visual_convergence_score and single-modality-fragment "
            "resolution are NOT measured/implemented -- see "
            "specification.md 'Implementation Status'."
        ),
        "uncaught_exception": uncaught_exception,
        "stage1_corpus_discovery": {
            "works": corpus,
            "total_expected_observation_points": total_expected,
            "total_present_observation_points": total_present,
        },
        "observation_bundle_completeness": completeness,
        "disambiguation_test_d": disambiguation,
        "replay_determinism": replay,
        "latency_at_scale": latency,
        "context_economy": context_economy,
        "cross_subject_technique_invariants": technique,
        "not_measured": {
            "visual_convergence_score": (
                "requires a real image-to-meaning measurement model; none "
                "exists anywhere in this workspace"
            ),
            "homotopy_hash_betti_numbers": "cle.homotopy is still Protocol-only",
            "cross_subject_technique_invariant_precision_P_invariant": (
                "requires a query benchmark with known relevant/irrelevant "
                "results, which does not exist"
            ),
            "single_modality_fragment_resolution": (
                "recognizing a raw crop/audio fragment as a specific work "
                "id would require a real image/audio recognition model; "
                "not implemented -- every reconstruction here starts from "
                "an already-resolved resolved_target_id"
            ),
        },
    }
    result["pass"] = bool(
        uncaught_exception is None
        and completeness.get("target_met")
        and disambiguation.get("pass")
        and replay.get("pass")
        and latency.get("pass")
    )
    return result


def main() -> None:
    result = run()
    output = Path(__file__).with_name("results") / "exp_hekb_005.json"
    output.parent.mkdir(exist_ok=True)
    output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
