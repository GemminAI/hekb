"""EXP-HEKB006 v2.1.0 -- Observer Invariance, Epistemic Agnosticism &
Reality-Driven Multi-Observer Convergence Validation.

Supersedes-by-extension EXP-HEKB006 v1.0.0's framing ("do 7 LLMs converge
on the same structure") with the specification's own v2.1.0 reframing: the
primary objective is **not** comparing LLMs, it is constructing and
verifying a model-agnostic **Reality Consensus Engine** -- a Pullback
Limit over typed morphisms (`_reality_consensus.py`, new) -- and proving it
works correctly whether or not any AI observer is available.

Per this experiment's own scope decision (mid-implementation instruction,
recorded here rather than silently assumed): "Observer APIs are optional.
If no external observers are available: execute all deterministic
mechanisms, execute all Human-vs-Human consensus tests, execute all
Reality Consensus tests, execute all registry and capability discovery,
execute all comparison algorithms using reusable HEKB artifacts, and
report only the unavailable observer-dependent metrics as BLOCKED."

This module does exactly that, over two real planes:

1. **Human plane (real, measured)** -- `_human_observers.py`'s three real,
   independently-authored channels already in EXP-HEKB005's real corpus
   (Critique/Wiki/MuseumCatalog), reused unmodified through
   `_semantic_closure.compute_closure` (EXP-HEKB002). Phase 1, Phase 3's
   real-data cross-check, and most of Tests A/C/D/E/F/G/I/J are measured
   here, on real data, not fabricated.
2. **AI-observer plane (real, honestly blocked)** -- `exp_hekb_006_cross_model.run()`
   (EXP-HEKB006 v1.0.0, reused unmodified, embedded whole as
   `cross_model_observer_plane_v1_0_0`): 0 of the 7 named LLM engines are
   callable in this workspace, a real environment finding that has not
   changed. Every metric that specifically requires a real AI observer
   (Test B, Test H, and the >=5-observer target of Test G) is reported
   `BLOCKED`, never estimated or defaulted to a passing value.

Also new: `_reality_consensus.py`'s own abstract `MechanismTest_*`
verification (Phase 3), which proves the Pullback Limit, Observer Bias
Index, leave-one-out robustness, blind-anonymization invariance, and
false-convergence guard are all wired correctly using a synthetic fixture
-- independent of whether any real observer (human or AI) is available,
exactly the same purpose EXP-HEKB006 v1.0.0's own Stage 4 already served
for `_cross_model_compare.py`.

No vector or embedding search anywhere. `src/hekb` not modified.
"""

from __future__ import annotations

import dataclasses
import json
from pathlib import Path
from typing import Any

import exp_hekb_006_cross_model as cross_model
from _cross_model_compare import proof_path_alignment
from _human_observers import HumanChannelResult, build_all_human_channels, observers_by_work
from _observer_registry import ObserverRecord, capability_summary, discover_registry
from _reality_consensus import (
    ObserverClosure,
    anonymize,
    compute_reality_consensus,
    false_convergence_check,
    leave_one_out_robustness,
    observer_bias_index,
)
from _semantic_closure import compute_closure
from _visual_corpus_fetch import WORK_CATALOG
from exp_hekb_006_cross_model import _mechanism_category


def run_phase1_human_ground_truth(
    channels: tuple[HumanChannelResult, ...],
    by_work: dict[str, tuple[ObserverClosure, ...]],
) -> dict[str, Any]:
    """Phase 1: real Human-vs-Human Ground Truth, built from 3 real
    independently-authored channels already in EXP-HEKB005's corpus (see
    `_human_observers.py`'s module docstring for why this is not
    fabrication) -- no live human-expert panel or LLM stands in for a
    human anywhere in this function."""
    per_channel = {
        result.channel: {
            "works_present": list(result.works_present),
            "works_absent": list(result.works_absent),
            "technique_links_found_in_own_text": {
                term: list(work_ids) for term, work_ids in result.technique_links.items()
            },
        }
        for result in channels
    }
    works_ge2 = {tid: obs for tid, obs in by_work.items() if len(obs) >= 2}
    per_work: dict[str, Any] = {}
    scores = []
    for target_id, observers in works_ge2.items():
        consensus = compute_reality_consensus(target_id, observers)
        per_work[target_id] = {
            "observer_count": len(observers),
            "observers": [oc.observer for oc in observers],
            "consensus_reality_score": consensus.consensus_reality_score,
            "intersection_object_count": len(consensus.intersection_object_ids),
            "union_object_count": len(consensus.union_object_ids),
        }
        scores.append(consensus.consensus_reality_score)
    return {
        "note": (
            "Human Expert Panel analogue: 3 real, independently-authored channels "
            "already present in EXP-HEKB005's real corpus (Critique/Wiki/MuseumCatalog), "
            "not a live human panel query and not an LLM standing in for a human. "
            "No text is generated by this experiment."
        ),
        "channels": per_channel,
        "works_with_multiple_real_human_observers": len(works_ge2),
        "works_with_single_observer_only": sorted(set(by_work) - set(works_ge2)),
        "per_work_consensus": per_work,
        "mean_consensus_reality_score": (sum(scores) / len(scores)) if scores else None,
        "min_consensus_reality_score": min(scores) if scores else None,
    }


def run_phase2_observer_infrastructure() -> tuple[dict[str, Any], tuple[ObserverRecord, ...]]:
    """Phase 2: the unified Observer Registry (`_observer_registry.py`)
    spanning both the real human plane and the 7 named LLM engines
    (`_observer_adapter.py`, reused unmodified)."""
    registry = discover_registry()
    report = {
        "registry": [dataclasses.asdict(r) for r in registry],
        "capability_summary_available_by_kind": capability_summary(registry),
        "total_registered": len(registry),
        "total_available": sum(1 for r in registry if r.available),
    }
    return report, registry


def run_phase3_consensus_mechanism() -> dict[str, Any]:
    """Phase 3: abstract, explicitly-labeled `MechanismTest_*` verification
    of `_reality_consensus.py` itself -- proves the Pullback Limit, OBI,
    leave-one-out robustness, blind-anonymization invariance, and
    false-convergence guard are wired correctly, independent of whether
    any real observer (human or AI) is available. Not a claim about real
    multi-observer convergence; see Phase 1 / Test A for the real-data
    measurement."""
    target_id = "MechanismTest_Q"
    shared_observations = ("MechanismTest_ObsA1", "MechanismTest_ObsA2")
    divergent_observations = ("MechanismTest_ObsD1",)

    def _closure_for(observation_ids: tuple[str, ...]) -> Any:
        category, relation_kind, object_category = _mechanism_category(target_id, observation_ids)
        return compute_closure(category, relation_kind, object_category, target_id)

    shared_closure = _closure_for(shared_observations)
    divergent_closure = _closure_for(divergent_observations)

    # 5 observers, matching the specification's own Test G threshold,
    # independently ingesting the IDENTICAL structure.
    identical_observers = tuple(
        ObserverClosure(observer=f"MechanismTest_Observer{i + 1}", closure=shared_closure)
        for i in range(5)
    )
    consensus_identical = compute_reality_consensus(target_id, identical_observers)
    obi_identical = {
        oc.observer: observer_bias_index(oc, consensus_identical) for oc in identical_observers
    }
    robustness_identical = leave_one_out_robustness(target_id, identical_observers)

    anonymized = anonymize(identical_observers)
    consensus_anonymized = compute_reality_consensus(target_id, anonymized)
    anonymization_invariant = (
        consensus_anonymized.consensus_reality_score == consensus_identical.consensus_reality_score
        and consensus_anonymized.intersection_object_ids
        == consensus_identical.intersection_object_ids
        and consensus_anonymized.intersection_morphism_triples
        == consensus_identical.intersection_morphism_triples
    )

    # 4 agreeing observers + 1 genuinely divergent one.
    mixed_observers = (
        *identical_observers[:4],
        ObserverClosure(observer="MechanismTest_ObserverDivergent", closure=divergent_closure),
    )
    consensus_mixed = compute_reality_consensus(target_id, mixed_observers)
    obi_mixed = {oc.observer: observer_bias_index(oc, consensus_mixed) for oc in mixed_observers}
    robustness_mixed = leave_one_out_robustness(target_id, mixed_observers)

    # False-convergence guard: a second, genuinely different mechanism
    # target must not merge with the first at consensus level.
    target_b_id = "MechanismTest_QB"
    category_b, relation_kind_b, object_category_b = _mechanism_category(
        target_b_id, ("MechanismTest_ObsB1",)
    )
    closure_b = compute_closure(category_b, relation_kind_b, object_category_b, target_b_id)
    consensus_b = compute_reality_consensus(
        target_b_id,
        (
            ObserverClosure(observer="MechanismTest_Observer1", closure=closure_b),
            ObserverClosure(observer="MechanismTest_Observer2", closure=closure_b),
        ),
    )
    false_convergence = false_convergence_check(consensus_identical, consensus_b)

    identical_pair_correct = (
        consensus_identical.consensus_reality_score == 1.0
        and all(v == 0.0 for v in obi_identical.values())
        and all(v == 1.0 for v in robustness_identical.values())
    )
    # OBI alone does not reliably rank the outlier here: OBI is the
    # fraction of an observer's OWN content outside the (now-smaller,
    # 5-way) consensus core, and the divergent observer's closure happens
    # to be smaller overall than the 4 agreeing observers' -- so a smaller
    # absolute overlap can still be a larger *fraction* of a smaller
    # closure. The real, robust discriminator is leave-one-out robustness:
    # removing the true outlier changes what the group agrees on a lot
    # (low Rob), while removing any one of the 4 agreeing observers barely
    # matters (the other 3 plus the outlier still pin the same small core).
    divergent_robustness = robustness_mixed["MechanismTest_ObserverDivergent"]
    agreeing_robustness = [robustness_mixed[oc.observer] for oc in mixed_observers[:4]]
    divergence_detected = (
        consensus_mixed.consensus_reality_score < consensus_identical.consensus_reality_score
        and divergent_robustness < min(agreeing_robustness)
    )

    return {
        "note": (
            "abstract mechanism-correctness check using MechanismTest_* identifiers, "
            "not real observer output -- proves _reality_consensus.py is wired "
            "correctly, independent of real observer availability"
        ),
        "identical_5_observer_consensus": dataclasses.asdict(consensus_identical),
        "identical_5_observer_obi": obi_identical,
        "identical_5_observer_leave_one_out_robustness": robustness_identical,
        "identical_pair_correctly_scored": identical_pair_correct,
        "blind_anonymization_invariant": anonymization_invariant,
        "mixed_4_agree_1_divergent_consensus": dataclasses.asdict(consensus_mixed),
        "mixed_observer_bias_indices": obi_mixed,
        "mixed_leave_one_out_robustness": robustness_mixed,
        "divergence_correctly_discriminated": divergence_detected,
        "false_convergence_guard": dataclasses.asdict(false_convergence),
        "pass": bool(
            identical_pair_correct
            and anonymization_invariant
            and divergence_detected
            and false_convergence.disambiguated
        ),
    }


def run_phase4_test_suite(
    by_work: dict[str, tuple[ObserverClosure, ...]],
    channels: tuple[HumanChannelResult, ...],
    phase3: dict[str, Any],
) -> dict[str, Any]:
    """Phase 4, Tests A-J. Each test is reported with an explicit
    `measured_on`/`status` field distinguishing real human-plane
    measurement from AI-plane `BLOCKED` findings -- never blended into one
    undifferentiated result."""
    works_ge2 = {tid: obs for tid, obs in by_work.items() if len(obs) >= 2}
    works_ge3 = {tid: obs for tid, obs in by_work.items() if len(obs) >= 3}
    wiki_channel = next(c for c in channels if c.channel == "Human_Wiki")
    artist_ids = frozenset(w.artist_slug for w in WORK_CATALOG)

    # Combined across every real channel's own text search -- e.g.
    # "impasto" is found in Human_Critique's own text for the two Vermeer
    # works, not Human_Wiki's; a per-work consensus's union includes
    # whatever any real channel contributed, so anything checked against
    # that union (Test E/J's legitimate-overlap whitelist) must combine
    # every channel too.
    all_technique_links: dict[str, set[str]] = {}
    for channel_result in channels:
        for term, work_ids in channel_result.technique_links.items():
            all_technique_links.setdefault(term, set()).update(work_ids)

    consensus_by_work = {tid: compute_reality_consensus(tid, obs) for tid, obs in works_ge2.items()}

    # Test A: Direct Observer Inter-Consistency.
    test_a_scores = {tid: c.consensus_reality_score for tid, c in consensus_by_work.items()}
    test_a = {
        "measured_on": "real Human_Critique / Human_Wiki / Human_MuseumCatalog channels",
        "per_work_consensus_reality_score": test_a_scores,
        "mean": (sum(test_a_scores.values()) / len(test_a_scores)) if test_a_scores else None,
        "llm_observer_plane": "BLOCKED -- 0/7 named LLM engines available",
    }

    # Test B: Open-Weights vs Proprietary Invariance -- purely an AI-plane test.
    test_b = {
        "status": "BLOCKED",
        "reason": (
            "requires >=1 open-weights AND >=1 proprietary LLM engine callable; 0/7 available"
        ),
    }

    # Test C: Cross-Observer Pullback Derivation -- real shared technique node.
    test_c = {
        "measured_on": (
            "Human_Wiki channel's real cross-work technique links (own text only); "
            "combined_across_all_channels additionally includes terms found only in "
            "another channel's own real text (e.g. Human_Critique)"
        ),
        "real_shared_technique_terms_wiki_channel_only": {
            term: list(work_ids) for term, work_ids in wiki_channel.technique_links.items()
        },
        "real_shared_technique_terms_combined_across_all_channels": {
            term: sorted(work_ids) for term, work_ids in all_technique_links.items()
        },
        "pass": len(wiki_channel.technique_links) > 0,
    }

    # Test D: Proof Path Equivalence -- real LCS alignment between per-channel
    # proof paths of the SAME real work.
    test_d_per_work: dict[str, dict[str, float]] = {}
    for target_id, observers in works_ge2.items():
        paths = {
            oc.observer: (
                f"resolved-target:{target_id}",
                *(c.formula for c in oc.closure.derived_compositions),
            )
            for oc in observers
        }
        names = list(paths)
        pairwise: dict[str, float] = {}
        for i in range(len(names)):
            for j in range(i + 1, len(names)):
                pairwise[f"{names[i]}_vs_{names[j]}"] = proof_path_alignment(
                    paths[names[i]], paths[names[j]]
                )
        test_d_per_work[target_id] = pairwise
    all_alignments = [v for pairwise in test_d_per_work.values() for v in pairwise.values()]
    test_d = {
        "measured_on": "real per-channel proof paths (derived_compositions)",
        "per_work_pairwise_alignment": test_d_per_work,
        "mean_alignment": (sum(all_alignments) / len(all_alignments)) if all_alignments else None,
    }

    # Test E: Disambiguation & False Convergence Guard, at consensus level,
    # over every real work pair with >=2 real observers.
    work_ids_sorted = sorted(consensus_by_work)
    false_convergence_results = []
    for i in range(len(work_ids_sorted)):
        for j in range(i + 1, len(work_ids_sorted)):
            a_id, b_id = work_ids_sorted[i], work_ids_sorted[j]
            shared_technique_ids = frozenset(
                f"technique/{term.replace(' ', '_')}"
                for term, work_ids in all_technique_links.items()
                if a_id in work_ids and b_id in work_ids
            )
            result = false_convergence_check(
                consensus_by_work[a_id],
                consensus_by_work[b_id],
                shared_structural_ids=artist_ids | shared_technique_ids,
            )
            false_convergence_results.append(dataclasses.asdict(result))
    rates = [r["false_convergence_rate"] for r in false_convergence_results]
    test_e = {
        "measured_on": "all real-work pairs with >=2 real human observers, consensus-level",
        "pairs_checked": len(false_convergence_results),
        "results": false_convergence_results,
        "all_disambiguated": all(r["disambiguated"] for r in false_convergence_results),
        "mean_false_convergence_rate": (sum(rates) / len(rates)) if rates else None,
    }

    # Test F: Blind Observer Independence.
    test_f_per_work = {}
    for target_id, observers in works_ge2.items():
        real_consensus = consensus_by_work[target_id]
        blind_consensus = compute_reality_consensus(target_id, anonymize(observers))
        test_f_per_work[target_id] = bool(
            real_consensus.consensus_reality_score == blind_consensus.consensus_reality_score
            and real_consensus.intersection_object_ids == blind_consensus.intersection_object_ids
        )
    test_f = {
        "measured_on": "real per-work consensus, observer labels anonymized before recomputation",
        "per_work_invariant": test_f_per_work,
        "all_invariant": all(test_f_per_work.values()) if test_f_per_work else None,
    }

    # Test G: Reality Consensus Engine Integration -- specification target
    # is >=5 independent observers; real human plane provides at most 3.
    max_observers_available = max((len(o) for o in by_work.values()), default=0)
    test_g = {
        "measured_on": (
            f"real human channels only, max {max_observers_available} observers per work"
        ),
        "specification_target_observer_count": 5,
        "real_observer_count_achieved": max_observers_available,
        "real_target_met": False,
        "reason_real_target_not_met": (
            "specification wants >=5 independent observers; this workspace provides at most "
            f"{max_observers_available} real human channels per work, and 0/7 named LLM engines "
            "are callable to supply the remaining observers"
        ),
        "mechanism_verified_at_5_observers": phase3["identical_pair_correctly_scored"],
    }

    # Test H: Human Expert Consensus Agreement -- needs a real AI-observer
    # consensus closure; none exists.
    test_h = {
        "status": "BLOCKED",
        "reason": (
            "R_expert_consensus requires a real AI-observer consensus closure to compare "
            "against the human ground truth closure; 0/7 named LLM engines are callable"
        ),
    }

    # Test I: Leave-One-Out Robustness -- real, for works with all 3 channels.
    test_i_per_work = {
        target_id: leave_one_out_robustness(target_id, works_ge3[target_id])
        for target_id in works_ge3
    }
    all_robustness = [v for per_observer in test_i_per_work.values() for v in per_observer.values()]
    test_i = {
        "measured_on": f"{len(works_ge3)} real works with all 3 human channels present",
        "per_work_per_observer_robustness": test_i_per_work,
        "mean_robustness": (sum(all_robustness) / len(all_robustness)) if all_robustness else None,
        "works_with_only_2_observers_excluded": sorted(set(works_ge2) - set(works_ge3)),
    }

    # Test J: Cross-Object Separation Guard -- same computation as Test E,
    # reported under its own specification name.
    test_j = {
        "measured_on": test_e["measured_on"],
        "pairs_checked": test_e["pairs_checked"],
        "false_convergence_rate_target": 0.0,
        "mean_false_convergence_rate": test_e["mean_false_convergence_rate"],
        "target_met": test_e["all_disambiguated"],
    }

    return {
        "test_a_direct_observer_inter_consistency": test_a,
        "test_b_open_weights_vs_proprietary": test_b,
        "test_c_cross_observer_pullback_derivation": test_c,
        "test_d_proof_path_equivalence": test_d,
        "test_e_disambiguation_false_convergence_guard": test_e,
        "test_f_blind_observer_independence": test_f,
        "test_g_reality_consensus_engine_integration": test_g,
        "test_h_human_expert_consensus_agreement": test_h,
        "test_i_leave_one_out_robustness": test_i,
        "test_j_cross_object_separation_guard": test_j,
    }


def run() -> dict[str, Any]:
    uncaught_exception: str | None = None
    try:
        channels = build_all_human_channels()
        by_work = observers_by_work(channels)
        phase1 = run_phase1_human_ground_truth(channels, by_work)
        phase2, _registry = run_phase2_observer_infrastructure()
        phase3 = run_phase3_consensus_mechanism()
        phase4 = run_phase4_test_suite(by_work, channels, phase3)
        cross_model_plane = cross_model.run()
    except Exception as exc:
        uncaught_exception = f"{type(exc).__name__}: {exc}"
        phase1 = phase2 = phase3 = phase4 = cross_model_plane = {"pass": False}

    result: dict[str, Any] = {
        "experiment": "EXP-HEKB006",
        "specification_version": "2.1.0",
        "scope": (
            "Reality Consensus Engine construction and verification across two real "
            "planes: (1) a real Human-vs-Human ground truth built from 3 independently-"
            "authored channels already in EXP-HEKB005's real corpus (Critique/Wiki/"
            "MuseumCatalog) -- Phase 1, most of Tests A/C/D/E/F/G/I/J, measured on real "
            "data; (2) the 7 named LLM engines from EXP-HEKB006 v1.0.0 (reused unmodified "
            "as cross_model_observer_plane_v1_0_0), 0/7 callable in this workspace -- "
            "Test B, Test H, and the >=5-observer target of Test G are BLOCKED on that "
            "finding, not fabricated. _reality_consensus.py (new) implements the "
            "specification's Pullback Limit / intersection-of-typed-morphisms consensus "
            "mathematics purely as set arithmetic over _semantic_closure.SemanticClosure "
            "(EXP-HEKB002, reused unmodified); no new retrieval algorithm, no vector or "
            "embedding search anywhere. src/hekb not modified."
        ),
        "uncaught_exception": uncaught_exception,
        "phase1_human_ground_truth": phase1,
        "phase2_observer_infrastructure": phase2,
        "phase3_reality_consensus_mechanism_verification": phase3,
        "phase4_test_suite_a_through_j": phase4,
        "cross_model_observer_plane_v1_0_0": cross_model_plane,
    }
    result["pass"] = bool(
        uncaught_exception is None
        and phase3.get("pass")
        and phase4.get("test_e_disambiguation_false_convergence_guard", {}).get("all_disambiguated")
        and phase4.get("test_f_blind_observer_independence", {}).get("all_invariant")
    )
    return result


def main() -> None:
    result = run()
    output = Path(__file__).with_name("results") / "exp_hekb_006.json"
    output.parent.mkdir(exist_ok=True)
    output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
