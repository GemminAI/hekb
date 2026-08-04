"""EXP-HEKB004 -- Multi-Modal Target Ingestion, Invariant Convergence &
Cross-Subject Retrieval Validation: design-stage orchestrator.

Builds on EXP-HEKB001 (persistence), EXP-HEKB002 (closed-loop validation),
and EXP-HEKB003 (real-world semantic search) without redesigning any of
them: retrieval reuses `_semantic_closure.compute_closure` (EXP-HEKB002)
unmodified via `_cross_modal_reconstruction.reconstruct` -- no vector or
embedding search, per explicit instruction.

**This run does not validate the specification's real 3x3 composer/work
matrix.** Stage 1 below scans the real corpus directory
(`experiments/EXP-HEKB004/corpus/`, or `$EXP_HEKB004_CORPUS_ROOT`) and
reports, honestly, what real files are actually present. As of this
design stage none are (see `specification.md`, "Implementation Status"):
Phases 1-3 and the eight §III metrics are therefore reported as
`blocked_on_real_corpus`, not fabricated, not simulated, and not silently
skipped. A separate `mechanism_verification` stage proves the
reconstruction engine itself is wired correctly, using clearly-labeled,
non-musical, abstract identifiers (`MechanismTest_*`) -- this is a code
correctness check, not a claim about real musical convergence, and must
not be read as one.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from _cross_modal_reconstruction import ReconstructionQuery, reconstruct, reconstruction_payload
from _multimodal_corpus import discover_corpus
from _observation_bundle import (
    ACOUSTICALLY_REALIZES,
    FORMALLY_DEFINES,
    AudioSlice,
    Observation,
    ScoreSlice,
    TargetHierarchy,
    TargetObject,
)
from hekb.category import KnowledgeCategory
from hekb.models import Concept, KnowledgeRelation

BLOCKED_REASON = (
    "no real audio (.mp3/.wav), score (.musicxml/.mid), or subtitle (.vtt) "
    "file, and no composer/work-specific critique or theory text, exists "
    "anywhere in this workspace for any of the 9 target works. Per this "
    "experiment's own 'do not fabricate' instruction and explicit direction "
    "from the requester, ingestion is paused until a real corpus is "
    "supplied under the contract in experiments/EXP-HEKB004/corpus/README.md."
)


def run_stage1_corpus_discovery() -> dict[str, Any]:
    manifest = discover_corpus()
    return manifest.as_dict()


def _blocked(phase: str) -> dict[str, Any]:
    return {
        "phase": phase,
        "status": "blocked_on_real_corpus",
        "reason": BLOCKED_REASON,
        "pass": False,
    }


def run_mechanism_verification() -> dict[str, Any]:
    """Prove `_cross_modal_reconstruction.reconstruct` is wired correctly
    -- real `hekb.category.KnowledgeCategory`, real
    `_semantic_closure.compute_closure`, real pushout traversal -- using
    abstract, explicitly non-musical identifiers. This is a mechanism
    correctness check, not a musical-convergence measurement; every id
    below is prefixed `MechanismTest_` so it cannot be mistaken for one.
    """
    category = KnowledgeCategory()
    target_id = "MechanismTest_Q"
    obs_a_id = "MechanismTest_ObsA"
    obs_b_id = "MechanismTest_ObsB"

    for concept_id in (target_id, obs_a_id, obs_b_id):
        category.add_object(Concept(id=concept_id, elements=frozenset({concept_id})))

    rel_a = KnowledgeRelation(
        id=f"{obs_a_id}_{ACOUSTICALLY_REALIZES}_{target_id}",
        source=obs_a_id,
        target=target_id,
        mapping={obs_a_id: target_id},
    )
    rel_b = KnowledgeRelation(
        id=f"{obs_b_id}_{FORMALLY_DEFINES}_{target_id}",
        source=obs_b_id,
        target=target_id,
        mapping={obs_b_id: target_id},
    )
    category.add_morphism(rel_a)
    category.add_morphism(rel_b)

    relation_kind = {rel_a.id: ACOUSTICALLY_REALIZES, rel_b.id: FORMALLY_DEFINES}
    object_category = {
        target_id: "MechanismTestTarget",
        obs_a_id: "MechanismTestObservation",
        obs_b_id: "MechanismTestObservation",
    }

    target = TargetObject(
        id=target_id,
        canonical_name="Mechanism Test Target -- not a real work",
        hierarchy=TargetHierarchy(composer="N/A (mechanism test)", work="N/A (mechanism test)"),
    )
    observations_by_id = {
        obs_a_id: Observation(
            modality="Audio",
            source_id="mechanism-test-fixture (not a real audio file)",
            slice=AudioSlice(time_range_s=(0.0, 1.0)),
            morphism_type=ACOUSTICALLY_REALIZES,
        ),
        obs_b_id: Observation(
            modality="Score",
            source_id="mechanism-test-fixture (not a real score file)",
            slice=ScoreSlice(measure_range="1-1"),
            morphism_type=FORMALLY_DEFINES,
        ),
    }

    result = reconstruct(
        category=category,
        relation_kind=relation_kind,
        object_category=object_category,
        query=ReconstructionQuery(
            raw_input="mechanism-self-check",
            input_modality="MechanismTest",
            resolved_target_id=target_id,
        ),
        target=target,
        observations_by_id=observations_by_id,
    )
    payload = reconstruction_payload(result)

    recovered_ids = {obs["source_id"] for obs in payload["observation_bundle"]}
    expected_ids = {observations_by_id[obs_a_id].source_id, observations_by_id[obs_b_id].source_id}
    bundle_complete = recovered_ids == expected_ids
    closure_minimal = result.closure.is_minimal_self_contained
    latency_measured_positive = result.search_metrics.execution_time_ms >= 0.0

    return {
        "note": "abstract mechanism correctness check, not real musical data",
        "payload": payload,
        "bundle_complete": bundle_complete,
        "closure_is_minimal_self_contained": closure_minimal,
        "latency_measured_ms": result.search_metrics.execution_time_ms,
        "pass": bool(bundle_complete and closure_minimal and latency_measured_positive),
    }


def run() -> dict[str, Any]:
    uncaught_exception: str | None = None
    try:
        corpus = run_stage1_corpus_discovery()
        mechanism = run_mechanism_verification()
    except Exception as exc:
        uncaught_exception = f"{type(exc).__name__}: {exc}"
        corpus = {}
        mechanism = {"pass": False}

    phase_1 = _blocked("Phase 1: Beethoven 3-work convergence (R_convergence)")
    phase_2 = _blocked(
        "Phase 2: 3-composer false-convergence & cross-subject retrieval "
        "(F_convergence, P_invariant)"
    )
    phase_3 = _blocked(
        "Phase 3: Cross-Modal Reconstruction Tests A-D (R_reconstruct, tau_multimodal, C(Q))"
    )

    result: dict[str, Any] = {
        "experiment": "EXP-HEKB004",
        "scope": (
            "Design-stage only: Observation Bundle model, typed-morphism "
            "vocabulary, real corpus directory contract, per-modality "
            "extractor Protocols, and the Cross-Modal Reconstruction Engine "
            "(reusing _semantic_closure.compute_closure from EXP-HEKB002 "
            "unmodified). No vector/embedding search anywhere. src/hekb not "
            "modified."
        ),
        "uncaught_exception": uncaught_exception,
        "stage1_corpus_discovery": corpus,
        "phase_1_beethoven_convergence": phase_1,
        "phase_2_cross_composer_validation": phase_2,
        "phase_3_cross_modal_reconstruction": phase_3,
        "mechanism_verification": mechanism,
        "blocked_reason": BLOCKED_REASON,
    }
    # Phases 1-3 are honestly blocked, not passed: the overall experiment
    # does not claim success while the real 3x3 matrix is unmeasured,
    # regardless of whether mechanism_verification and corpus discovery
    # themselves ran cleanly.
    result["pass"] = False
    return result


def main() -> None:
    result = run()
    output = Path(__file__).with_name("results") / "exp_hekb_004.json"
    output.parent.mkdir(exist_ok=True)
    output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
