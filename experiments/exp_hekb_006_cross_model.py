"""EXP-HEKB006 -- Cross-Model Epistemic Invariance & Multi-LLM Epistemic
Convergence Validation.

Builds on EXP-HEKB001 (persistence), EXP-HEKB002 (closed-loop validation +
`_semantic_closure.compute_closure`), EXP-HEKB003 (real-world semantic
search, software artifact corpus), EXP-HEKB004 (multi-modal design,
blocked on a real corpus), and EXP-HEKB005 (real visual corpus) without
redesigning any of them.

**Real, checked finding this experiment's own Stage 1 makes**: of the 7
named observer engines (Gemma, Qwen, Llama, Mistral, Claude, GPT, Gemini),
zero have real, callable access in this workspace -- no local model
runtime (`ollama`, `llama_cpp`) and no API credential for any of them (see
`_observer_adapter.probe_observer_availability`, a real environment
check, not an assumption). Per the specification's own "DO NOT fabricate
outputs ... mark the observer unavailable ... continue with available
observers" instruction, this run continues with the 0 available
observers it actually has: real observer-availability probing (Stage 1),
real inventory of the corpora EXP-HEKB003/004/005 already prepared for
future cross-model ingestion (Stage 2), a real per-engine call attempt
that documents exactly why each fails (Stage 3), and an abstract
`MechanismTest_*`-labeled mechanism-correctness check of the new
`_cross_model_compare.py` comparison engine (Stage 4) -- explicitly not a
claim about real cross-model convergence. Every one of specification
section III's 7 target metrics is therefore reported `NOT MEASURED`, with
the specific real reason each requires (never a fabricated number).

Separately: even if a real observer's text became available today, this
workspace still has no real Meaning Mapper to project arbitrary natural
language into a `msr.abi.MeaningMeasurement` -- the same gap
`docs/RFC_ALIGNMENT.md` (EXP-HEKB002-005) already recorded, now blocking
the ingestion side of this pipeline too. See `_cross_model_runner.py`.
"""

from __future__ import annotations

import dataclasses
import json
from pathlib import Path
from typing import Any

from _cross_model_compare import compare
from _cross_model_runner import ObserverRunResult, run_all_observers
from _multimodal_corpus import discover_corpus as discover_multimodal_corpus
from _observer_adapter import ObserverAvailability, probe_observer_availability
from _real_corpus import build_real_property_graph
from _real_visual_extractors import discover_visual_corpus
from _semantic_closure import SemanticClosure, compute_closure
from _visual_corpus_fetch import WORK_CATALOG as VISUAL_WORK_CATALOG
from hekb.category import KnowledgeCategory
from hekb.models import Concept, KnowledgeRelation

BLOCKED_REASON = (
    "0 of 7 named observer engines (Gemma, Qwen, Llama, Mistral, Claude, GPT, Gemini) have real, "
    "callable access in this workspace -- no local model runtime (`ollama`, `llama_cpp`) and no "
    "API credential for any of them (see stage1_observer_availability). Per the specification's "
    "own 'do not fabricate' instruction, cross-model convergence cannot be measured with 0 real "
    "observer outputs."
)

TARGET_PROMPT = (
    "Describe the sfumato technique as manifested in Leonardo da Vinci's Mona Lisa "
    "(real EXP-HEKB005 corpus target: da_vinci/mona_lisa)."
)


def run_stage1_observer_availability() -> tuple[ObserverAvailability, ...]:
    return probe_observer_availability()


def run_stage2_corpus_inventory() -> dict[str, Any]:
    """Real inventory of what EXP-HEKB003/004/005 already prepared --
    corpora this experiment would ingest per-observer once a real observer
    exists, not re-fetched or re-derived here."""
    visual_statuses = discover_visual_corpus(VISUAL_WORK_CATALOG)
    visual_present = sum(s.present_count for s in visual_statuses)
    visual_expected = sum(len(s.files) for s in visual_statuses)

    multimodal_manifest = discover_multimodal_corpus()

    graph, survey = build_real_property_graph()

    return {
        "visual_corpus_exp_hekb_005": {
            "works": len(visual_statuses),
            "observation_points_present": visual_present,
            "observation_points_expected": visual_expected,
            "note": "real 3-painter x 3-work visual+text corpus already ingested by EXP-HEKB005",
        },
        "multimodal_corpus_exp_hekb_004": {
            **multimodal_manifest.as_dict(),
            "note": "real 3-composer x 3-work audio/score/critique corpus; still 0 files present",
        },
        "software_artifact_corpus_exp_hekb_003": {
            "survey": survey.as_dict(),
            "node_count": len(graph.nodes),
            "edge_count": len(graph.edges),
            "note": "real 3-repository software artifact corpus already ingested by EXP-HEKB003",
        },
    }


def run_stage3_observer_attempts() -> tuple[ObserverRunResult, ...]:
    return run_all_observers(TARGET_PROMPT)


def _mechanism_category(
    target_id: str, observation_ids: tuple[str, ...], morphism_type: str = "observes"
) -> tuple[KnowledgeCategory, dict[str, str], dict[str, str]]:
    """One abstract, explicitly-labeled `MechanismTest_*` observer
    ingestion: a target plus its observations, each one real morphism hop
    away -- the same shape every EXP-HEKB00{2,4,5} mechanism fixture
    already used. Not real observer output."""
    category = KnowledgeCategory()
    category.add_object(Concept(id=target_id, elements=frozenset({target_id})))
    relation_kind: dict[str, str] = {}
    object_category: dict[str, str] = {target_id: "MechanismTestTarget"}
    for observation_id in observation_ids:
        category.add_object(Concept(id=observation_id, elements=frozenset({observation_id})))
        object_category[observation_id] = "MechanismTestObservation"
        relation = KnowledgeRelation(
            id=f"{observation_id}_{morphism_type}_{target_id}",
            source=observation_id,
            target=target_id,
            mapping={observation_id: target_id},
        )
        category.add_morphism(relation)
        relation_kind[relation.id] = morphism_type
    return category, relation_kind, object_category


def _proof_path_of(closure: SemanticClosure, target_id: str) -> tuple[str, ...]:
    return (f"resolved-target:{target_id}", *(c.formula for c in closure.derived_compositions))


def run_stage4_mechanism_verification() -> dict[str, Any]:
    """Proves `_cross_model_compare.py`'s comparison engine is wired
    correctly -- real `hekb.category.KnowledgeCategory` instances, real
    `_semantic_closure.compute_closure` (EXP-HEKB002, unmodified), real
    comparison arithmetic -- using abstract `MechanismTest_*` identifiers.
    This is a code-correctness check, not a claim about real cross-model
    convergence, and must not be read as one.

    Two scenarios: `MechanismTest_ObserverA`/`MechanismTest_ObserverB`
    independently ingest the identical structure (simulating what real
    convergence onto the same HEKB object ids would look like), and
    `MechanismTest_ObserverC` ingests a genuinely different structure
    (simulating real divergence) -- proving the comparison metrics
    actually discriminate rather than always returning a fixed value.
    """
    target_id = "MechanismTest_Q"
    shared_observations = ("MechanismTest_ObsA1", "MechanismTest_ObsA2")
    divergent_observations = ("MechanismTest_ObsC1",)

    category_a, rk_a, oc_a = _mechanism_category(target_id, shared_observations)
    category_b, rk_b, oc_b = _mechanism_category(target_id, shared_observations)
    category_c, rk_c, oc_c = _mechanism_category(target_id, divergent_observations)

    closure_a = compute_closure(category_a, rk_a, oc_a, target_id)
    closure_b = compute_closure(category_b, rk_b, oc_b, target_id)
    closure_c = compute_closure(category_c, rk_c, oc_c, target_id)

    comparison_identical = compare(
        "MechanismTest_ObserverA",
        closure_a,
        _proof_path_of(closure_a, target_id),
        None,
        "MechanismTest_ObserverB",
        closure_b,
        _proof_path_of(closure_b, target_id),
        None,
    )
    comparison_divergent = compare(
        "MechanismTest_ObserverA",
        closure_a,
        _proof_path_of(closure_a, target_id),
        None,
        "MechanismTest_ObserverC",
        closure_c,
        _proof_path_of(closure_c, target_id),
        None,
    )

    identical_pair_correct = (
        comparison_identical.closure_structure_similarity == 1.0
        and comparison_identical.morphism_graph_edit_distance == 0.0
        and comparison_identical.pullback_pushout_identity_rate == 1.0
        and comparison_identical.proof_path_alignment == 1.0
        and comparison_identical.invariant_identity is None
    )
    divergent_pair_detected = (
        comparison_divergent.closure_structure_similarity < 1.0
        and comparison_divergent.morphism_graph_edit_distance > 0.0
    )

    return {
        "note": (
            "abstract mechanism correctness check using MechanismTest_* identifiers, "
            "not real observer output -- proves _cross_model_compare.py is wired correctly, "
            "independent of whether any real observer is available"
        ),
        "comparison_identical_structure": dataclasses.asdict(comparison_identical),
        "comparison_divergent_structure": dataclasses.asdict(comparison_divergent),
        "identical_pair_correctly_scored": identical_pair_correct,
        "divergent_pair_correctly_discriminated": divergent_pair_detected,
        "pass": bool(identical_pair_correct and divergent_pair_detected),
    }


def _blocked(name: str) -> dict[str, Any]:
    return {
        "name": name,
        "status": "blocked_on_real_observers",
        "reason": BLOCKED_REASON,
        "pass": False,
    }


def run_phased_execution_matrix() -> dict[str, Any]:
    return {
        "phase_1_gemma_vs_claude_3_masterworks": _blocked(
            "Phase 1: 2 models (Gemma vs Claude) x 3 masterworks (EXP-HEKB005)"
        ),
        "phase_2_seven_models_all_corpora": _blocked(
            "Phase 2: 7 models x all corpora (GED_morphism, R_limit_identity)"
        ),
        "phase_3_full_invariance_suite": _blocked(
            "Phase 3: Full Cross-Model Invariance Suite (Tests A-E)"
        ),
    }


def run_model_invariance_test_suite() -> dict[str, Any]:
    return {
        "test_a_direct_model_inter_consistency": _blocked("Test A: Direct Model Inter-Consistency"),
        "test_b_open_weights_vs_proprietary": _blocked(
            "Test B: Open-Weights vs Proprietary Invariance"
        ),
        "test_c_cross_model_pullback_derivation": _blocked(
            "Test C: Cross-Model Pullback Derivation"
        ),
        "test_d_proof_path_equivalence": _blocked("Test D: Proof Path Equivalence"),
        "test_e_model_disambiguation_guard": _blocked("Test E: Model Disambiguation Guard"),
    }


def run_target_metrics() -> dict[str, Any]:
    """Specification section III's 7 target metrics -- every one requires
    >=2 real, per-observer `SemanticClosure`s (or completeness/latency
    samples); this run has 0 real observers, so every metric is honestly
    `NOT MEASURED`, not estimated, not defaulted to a passing value."""
    return {
        "I_cross_model_invariant_identity": {
            "status": "NOT MEASURED",
            "reason": (
                "requires >=2 real per-observer InvariantSignature.homotopy_hash values; "
                "cle.homotopy is still Protocol-only (EXP-HEKB002-005's recorded gap) and 0 real "
                "observers exist to produce a signature from regardless"
            ),
        },
        "S_closure_sim_closure_structure_similarity": {
            "status": "NOT MEASURED",
            "reason": "requires >=2 real per-observer SemanticClosures; 0 real observers exist",
        },
        "GED_morphism_graph_edit_distance": {
            "status": "NOT MEASURED",
            "reason": "requires >=2 real per-observer SemanticClosures; 0 real observers exist",
        },
        "R_limit_identity_pullback_pushout": {
            "status": "NOT MEASURED",
            "reason": "requires >=2 real per-observer SemanticClosures; 0 real observers exist",
        },
        "P_proof_align_proof_path_alignment": {
            "status": "NOT MEASURED",
            "reason": "requires >=2 real per-observer proof_paths; 0 real observers exist",
        },
        "Var_C_obs_cross_model_observation_completeness": {
            "status": "NOT MEASURED",
            "reason": (
                "variance across models is undefined for 0 real per-observer completeness "
                "values (see _cross_model_compare.completeness_variance, which returns None "
                "below 2 values rather than a misleading 0.0)"
            ),
        },
        "tau_variance_cross_model_retrieval_latency": {
            "status": "NOT MEASURED",
            "reason": "same reason as Var(C_obs): 0 real per-observer latency samples exist",
        },
    }


def run() -> dict[str, Any]:
    uncaught_exception: str | None = None
    try:
        availability = run_stage1_observer_availability()
        corpus_inventory = run_stage2_corpus_inventory()
        observer_attempts = run_stage3_observer_attempts()
        mechanism = run_stage4_mechanism_verification()
    except Exception as exc:
        uncaught_exception = f"{type(exc).__name__}: {exc}"
        availability = ()
        corpus_inventory = {}
        observer_attempts = ()
        mechanism = {"pass": False}

    available_count = sum(1 for a in availability if a.available)

    result: dict[str, Any] = {
        "experiment": "EXP-HEKB006",
        "scope": (
            "Cross-model epistemic invariance validation across 7 named observer engines (Gemma, "
            "Qwen, Llama, Mistral, Claude, GPT, Gemini). Reuses _semantic_closure.compute_closure "
            "(EXP-HEKB002) unmodified for all structural comparison; adds no new retrieval "
            "algorithm. No vector or embedding search anywhere. src/hekb not modified. A real "
            "environment probe found 0 of 7 observers callable in this workspace; every "
            "specification section III metric is therefore NOT MEASURED, not fabricated -- see "
            "stage1_observer_availability and target_metrics."
        ),
        "uncaught_exception": uncaught_exception,
        "stage1_observer_availability": [dataclasses.asdict(a) for a in availability],
        "stage1_available_observer_count": available_count,
        "stage2_corpus_inventory": corpus_inventory,
        "stage3_observer_attempts": [dataclasses.asdict(r) for r in observer_attempts],
        "stage4_mechanism_verification": mechanism,
        "phased_execution_matrix": run_phased_execution_matrix(),
        "model_invariance_test_suite": run_model_invariance_test_suite(),
        "target_metrics": run_target_metrics(),
        "blocked_reason": BLOCKED_REASON,
    }
    # The real objective (measured cross-model convergence) is entirely
    # unmeasured with 0 real observers -- "pass" stays False regardless of
    # whether Stage 1-4 (all real, all honestly computed) ran cleanly,
    # exactly matching EXP-HEKB004's precedent for a blocked experiment.
    result["pass"] = False
    return result


def main() -> None:
    result = run()
    output = Path(__file__).with_name("results") / "exp_hekb_006.json"
    output.parent.mkdir(exist_ok=True)
    output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
