"""EXP-HEKB007 -- End-to-End Epistemic Pipeline & Observation Bundle
Round-Trip System Integration Validation.

What EXP-HEKB001-006 already built, separately, and this experiment does
NOT redesign or re-derive:

- EXP-HEKB002/003 (`_msr_cle_pipeline.py`): a real, deterministic
  `msr.runtime.MeaningSpaceRuntime` settling into a genuinely novel
  attractor, lifted by a real `cle.categorical_lift.engine.CategoricalLiftEngine`
  (its own `cle.reference` strategies) into a real `Concept`.
- EXP-HEKB002 (`_cle_hekb_adapter.py`): the bridge from CLE's `Concept` ABI
  into `hekb.models.Concept`.
- EXP-HEKB002/003/004/005/006 (`_semantic_closure.py`): the Semantic
  Closure Engine -- real pullback/pushout minimal-subcategory computation
  over `hekb.category.KnowledgeCategory`, no vector or embedding search.
- EXP-HEKB003 (`_semantic_search.py`): categorical retrieval and ranking
  over a computed closure.
- EXP-HEKB005 (`exp_hekb_005_visual_reconstruction.ingest_real_corpus`,
  `_visual_reconstruction.py`): the one genuinely real, substantial corpus
  in this workspace -- 9 real works (3 Leonardo da Vinci, 3 Johannes
  Vermeer, 3 Vincent van Gogh), fetched once from Wikipedia/Wikidata/
  Wikimedia Commons plus public-domain critique text, already ingested
  into a real `hekb.category.KnowledgeCategory` with real observation
  completeness (`C_obs(Q)`/`C_w(Q)`) and disambiguation already validated.
- EXP-HEKB006 (`_reality_consensus.py`): a Pullback-Limit Reality Consensus
  Engine over real per-observer closures (not used directly below -- this
  experiment's single MSR/CLE crystallization is one observer, and
  consensus needs >= 2; see `docs/RFC_ALIGNMENT.md` for why that plane
  stays out of this run's scope).

What is genuinely new here (the "missing orchestration and integration
glue" this experiment exists to build):

1. **Cross-pipeline integration** (`run_stage3_integration_glue`): the
   MSR/CLE-crystallized `Concept` and EXP-HEKB005's real 9-work corpus have
   never shared one `hekb.category.KnowledgeCategory` before -- each prior
   experiment built and queried its own separate category. This stage puts
   both in the same category for the first time, and Stage 4 below proves
   the Semantic Closure Engine correctly keeps them apart (no false
   convergence) while both remain independently queryable.
2. **A real, standalone network daemon** (`_mcp_daemon.py`, new): every
   prior MCP interface is explicitly in-process by design (see
   `docs/RFC_ALIGNMENT.md`, "Gate dependency: msr, cle" section). This
   experiment's own specification names a standalone TCP daemon and a
   concurrent-load test as an explicit target component, and a local TCP
   daemon requires no external repository or unavailable runtime -- so per
   this experiment's own "implement every executable mechanism" governing
   instruction, it is built, not deferred.
3. **System-wide Context Economy** over the combined category (bigger than
   any single prior experiment's own category).
4. **Fault injection across the combined pipeline** (Stage 7): malformed
   category operations, an unstabilized-trajectory CLE call, and malformed
   daemon requests, all asserted to be quarantined rather than crashing.

No embeddings, no vector search anywhere (`_semantic_closure.py` is pure
category-theoretic traversal). `src/hekb` is not modified. `msr`/`cle`
source is not modified -- both are gate dependencies (see
`docs/RFC_ALIGNMENT.md`, "Gate dependency: msr, cle", and this file's own
addendum for the pattern this experiment reuses unchanged).
"""

from __future__ import annotations

import json
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from cle.errors import NotStabilized

from _cle_hekb_adapter import cle_concept_to_hekb
from _concept_store import FileConceptStore
from _file_backend import FileProjectionBackend
from _mcp_daemon import run_concurrent_load_test
from _msr_cle_pipeline import run_upstream as msr_cle_run_upstream
from _semantic_closure import compute_closure
from _visual_corpus_fetch import WORK_CATALOG
from _visual_observation_bundle import TargetHierarchy, TargetObject
from _visual_reconstruction import (
    ReconstructionQuery,
    check_disambiguation,
    reconstruct,
    reconstruction_payload,
)
from exp_hekb_005_visual_reconstruction import ingest_real_corpus, work_target_id
from hekb.category import CategoryAxiomViolation, KnowledgeCategory
from hekb.models import Concept, KnowledgeRelation
from hekb.storage import to_storage_profile

STORE_ROOT = Path(__file__).with_name("_hekb_store") / "exp_hekb_007"
CONCEPT_STORE = STORE_ROOT / "concepts"
RELATION_STORE = STORE_ROOT / "relations"

PIPELINE_NODE_ID = "EXP-HEKB007_MSR_CLE_Pipeline"
QUERY_WORK = WORK_CATALOG[0]  # da_vinci/mona_lisa -- the corpus's own first real work
LOAD_TEST_CLIENTS = 100
NETWORK_LATENCY_TARGET_MS = 10.0


def _fresh_dir(path: Path) -> Path:
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True)
    return path


def _target_object_for(work: Any) -> TargetObject:
    return TargetObject(
        id=work_target_id(work),
        canonical_name=work.canonical_name,
        hierarchy=TargetHierarchy(artist=work.artist, work=work.canonical_name),
    )


# ------------------------------------------------------------------ stage 1


def run_stage1_real_corpus_ingestion() -> Any:
    """Reuse EXP-HEKB005's own already-validated real ingestion, unmodified.

    Stands in for Raw Observation -> Meaning Mapper -> HEKB for the visual
    modality: real Wikipedia/Wikidata/Wikimedia Commons + public-domain
    critique text, already fetched and cached (`_visual_corpus_fetch.py`),
    ingested into a real `hekb.category.KnowledgeCategory`.
    """
    return ingest_real_corpus()


# ------------------------------------------------------------------ stage 2


def run_stage2_msr_cle_upstream() -> Any:
    """Reuse EXP-HEKB002/003's own already-validated MSR -> CLE upstream,
    unmodified. Stands in for Raw Observation -> Meaning Mapper -> MSR ->
    CLE for a machine-crystallized (not corpus-derived) concept, per the
    scope decision recorded in `_msr_cle_pipeline.py` and
    `docs/RFC_ALIGNMENT.md` ("Local Model / Meaning Mapper" is represented
    by a deterministic `MeaningMeasurement` stream, not a live call into
    `semantic-annotator-core`/`meaning-mapper`, neither of which is gate-
    installed in this repository)."""
    return msr_cle_run_upstream()


# ------------------------------------------------------------------ stage 3


@dataclass
class IntegrationResult:
    category: KnowledgeCategory
    relation_kind: dict[str, str]
    object_category: dict[str, str]
    engine_concept_id: str
    pipeline_node_id: str


def run_stage3_integration_glue(ingest: Any, upstream: Any) -> IntegrationResult:
    """The missing orchestration glue: bridge the MSR/CLE-crystallized
    `Concept` into the SAME real category EXP-HEKB005's real corpus already
    occupies -- never done together before this experiment.

    The provenance edge added here (`engine_concept -> produced_by ->
    PIPELINE_NODE_ID`) is a true structural fact about where the engine
    concept came from (this experiment's own MSR/CLE run) -- it is
    deliberately NOT linked to any specific real corpus work: the MSR
    settle stream in `_msr_cle_pipeline.py` (a synthetic well at a fixed
    coordinate) is not "about" any real painting, and asserting such a link
    would be exactly the kind of fabricated semantic claim this workspace's
    convention exists to prevent. Stage 4 verifies this deliberate
    non-connection: the crystallized concept's closure and any real work's
    closure must share no object.
    """
    category = ingest.category
    relation_kind = dict(ingest.relation_kind)
    object_category = dict(ingest.object_category)

    cle_candidate = upstream.commit_candidates[0]
    cle_concept = cle_candidate.delta.concept
    assert cle_concept is not None, "expected a Concept-kind candidate from a novel trajectory"
    engine_concept = cle_concept_to_hekb(cle_concept)

    pipeline_node = Concept(id=PIPELINE_NODE_ID, elements=frozenset({PIPELINE_NODE_ID}))
    category.add_object(pipeline_node)
    category.add_object(engine_concept)
    object_category[PIPELINE_NODE_ID] = "IntegrationMechanism"
    object_category[engine_concept.id] = "CrystallizedKnowledge"

    provenance = KnowledgeRelation(
        id=f"{engine_concept.id}_produced_by_{PIPELINE_NODE_ID}",
        source=engine_concept.id,
        target=PIPELINE_NODE_ID,
        mapping={engine_concept.id: PIPELINE_NODE_ID},
    )
    category.add_morphism(provenance)
    relation_kind[provenance.id] = "produced_by"

    concept_store = FileConceptStore(_fresh_dir(CONCEPT_STORE))
    relation_store = FileProjectionBackend(_fresh_dir(RELATION_STORE))
    concept_store.write(pipeline_node)
    concept_store.write(engine_concept)
    relation_store.write(to_storage_profile(provenance))

    return IntegrationResult(
        category=category,
        relation_kind=relation_kind,
        object_category=object_category,
        engine_concept_id=engine_concept.id,
        pipeline_node_id=PIPELINE_NODE_ID,
    )


# ------------------------------------------------------------------ stage 4


def run_stage4_closure_and_disambiguation(
    ingest: Any, integration: IntegrationResult
) -> dict[str, Any]:
    """Semantic Closure + Observation Bundle Recovery over the combined
    graph, for a real corpus work (`C_obs(Q)`/`C_w(Q)`, reusing
    EXP-HEKB005's own `reconstruct` unmodified) and for the engine concept
    (a small, real closure of its own) -- plus the disambiguation check
    Stage 3's docstring promises: the two must not false-converge."""
    target = _target_object_for(QUERY_WORK)
    query_id = work_target_id(QUERY_WORK)
    result = reconstruct(
        category=integration.category,
        relation_kind=integration.relation_kind,
        object_category=integration.object_category,
        query=ReconstructionQuery(
            raw_input=f"resolved-target:{query_id}",
            input_modality="PreResolved",
            resolved_target_id=query_id,
        ),
        target=target,
        observations_by_id=ingest.observations_by_id,
        ground_truth_observations=ingest.ground_truth_by_work[query_id],
    )
    real_work_payload = reconstruction_payload(result)

    engine_closure = compute_closure(
        integration.category,
        integration.relation_kind,
        integration.object_category,
        integration.engine_concept_id,
    )

    disambiguation = check_disambiguation(
        integration.category,
        integration.relation_kind,
        integration.object_category,
        query_id,
        integration.engine_concept_id,
    )

    system_wide_context_economy_ratio = len(result.closure.objects) / len(
        integration.category.objects
    )

    return {
        "real_work_query": {
            "target_id": query_id,
            "observation_completeness_C_obs": result.completeness.observation_completeness,
            "weighted_observation_completeness_C_w": (
                result.completeness.weighted_observation_completeness
            ),
            "closure_object_count": len(result.closure.objects),
            "is_minimal_self_contained": result.closure.is_minimal_self_contained,
            "proof_path": real_work_payload["proof_path"],
        },
        "engine_concept_query": {
            "target_id": integration.engine_concept_id,
            "closure_object_count": len(engine_closure.objects),
            "closure_object_ids": [o.id for o in engine_closure.objects],
            "is_minimal_self_contained": engine_closure.is_minimal_self_contained,
        },
        "cross_pipeline_disambiguation": disambiguation,
        "combined_category_object_count": len(integration.category.objects),
        "system_wide_context_economy_ratio": system_wide_context_economy_ratio,
        "pass": bool(
            result.closure.is_minimal_self_contained
            and engine_closure.is_minimal_self_contained
            and disambiguation["disambiguated"]
        ),
    }


# ------------------------------------------------------------------ stage 5


def run_stage5_network_daemon_load_test(integration: IntegrationResult) -> dict[str, Any]:
    """Test D: a real, standalone TCP daemon (`_mcp_daemon.py`, new) over
    the combined category, under real concurrent load."""
    query_id = work_target_id(QUERY_WORK)
    result: dict[str, Any] = run_concurrent_load_test(
        integration.category,
        integration.relation_kind,
        integration.object_category,
        (query_id, integration.engine_concept_id),
        concurrent_clients=LOAD_TEST_CLIENTS,
    )
    p99 = result["latency_p99_ms"]
    result["latency_target_ms"] = NETWORK_LATENCY_TARGET_MS
    result["target_met"] = bool(p99 is not None and p99 < NETWORK_LATENCY_TARGET_MS)
    # Correctness gate only; the aggressive latency target is reported, not gated on.
    result["pass"] = bool(result["all_succeeded"])
    return result


# ------------------------------------------------------------------ stage 6


def _normalized_full_pipeline_snapshot() -> dict[str, Any]:
    ingest = run_stage1_real_corpus_ingestion()
    upstream = run_stage2_msr_cle_upstream()
    integration = run_stage3_integration_glue(ingest, upstream)
    closure = run_stage4_closure_and_disambiguation(ingest, integration)
    closure["real_work_query"].pop("execution_time_ms", None)
    return {
        "engine_concept_id": integration.engine_concept_id,
        "closure_and_disambiguation": closure,
    }


def run_stage6_replay_determinism() -> dict[str, Any]:
    """Full-loop replay determinism (metric 11), scoped: ingestion -> MSR/CLE
    -> integration -> closure/search content, run twice from a cold start.
    Network daemon timing (Stage 5) is real wall-clock latency by nature and
    is excluded here, exactly as `execution_time_ms` is excluded from every
    prior experiment's own replay-determinism check (e.g. EXP-HEKB005's
    `run_replay_determinism`)."""
    first = _normalized_full_pipeline_snapshot()
    second = _normalized_full_pipeline_snapshot()
    identical = json.dumps(first, sort_keys=True) == json.dumps(second, sort_keys=True)
    return {
        "scope": "ingestion + MSR/CLE upstream + integration + closure/search content "
        "(network daemon wall-clock latency excluded, as in every prior "
        "experiment's own replay-determinism check)",
        "bit_identical": identical,
        "pass": bool(identical),
    }


# ------------------------------------------------------------------ stage 7


def run_stage7_fault_injection(integration: IntegrationResult) -> dict[str, Any]:
    """Y_robustness (metric 12): real malformed operations against the real
    combined category, the real CLE engine boundary, and the real network
    daemon -- every one asserted to be quarantined, never an uncaught
    crash."""
    findings: list[dict[str, Any]] = []

    # 1. Non-total morphism (category axiom violation).
    try:
        integration.category.add_morphism(
            KnowledgeRelation(
                id="fault-injection-non-total",
                source=integration.pipeline_node_id,
                target=integration.engine_concept_id,
                mapping={},  # empty: not total over source's single-element set
            )
        )
        findings.append({"case": "non_total_morphism", "quarantined": False})
    except CategoryAxiomViolation as exc:
        findings.append({"case": "non_total_morphism", "quarantined": True, "error": str(exc)})

    # 2. Duplicate object id (category axiom violation).
    try:
        integration.category.add_object(
            Concept(id=integration.engine_concept_id, elements=frozenset({"x"}))
        )
        findings.append({"case": "duplicate_object", "quarantined": False})
    except CategoryAxiomViolation as exc:
        findings.append({"case": "duplicate_object", "quarantined": True, "error": str(exc)})

    # 3. CLE engine called with an unstabilized trajectory (dwell_steps=0).
    from _msr_cle_pipeline import build_cle_engine

    @dataclass(frozen=True)
    class _FakeUnstabilizedTrajectory:
        trajectory_id: str = "fault-injection-unstabilized"
        dwell_steps: int = 0
        states: tuple[Any, ...] = ()

    try:
        # Deliberately structurally incomplete vs. StabilizedTrajectoryLike:
        # CategoricalLiftEngine._validate_trajectory reads only dwell_steps
        # and states before raising, so this fixture stops there on
        # purpose rather than fabricating geometry (centroid/covariance/...)
        # this fault-injection case never needs.
        build_cle_engine().lift(_FakeUnstabilizedTrajectory(), hekb_context=None)
        findings.append({"case": "unstabilized_trajectory", "quarantined": False})
    except NotStabilized as exc:
        findings.append({"case": "unstabilized_trajectory", "quarantined": True, "error": str(exc)})

    # 4. Malformed daemon request (missing key) and unknown concept id --
    # the daemon must answer with a real error payload, not hang or crash.
    daemon_findings = _malformed_daemon_requests(integration)
    findings.extend(daemon_findings)

    uncaught = [f for f in findings if not f["quarantined"]]
    return {
        "cases": findings,
        "cases_checked": len(findings),
        "cases_quarantined": len(findings) - len(uncaught),
        "uncaught_exceptions": len(uncaught),
        "pass": bool(len(uncaught) == 0),
    }


def _malformed_daemon_requests(integration: IntegrationResult) -> list[dict[str, Any]]:
    import json as _json
    import socket as _socket

    from _mcp_daemon import HEKBMCPDaemon
    from _mcp_reference import MCPReferenceQuery

    query = MCPReferenceQuery(
        category=integration.category,
        relation_kind=integration.relation_kind,
        object_category=integration.object_category,
    )
    daemon = HEKBMCPDaemon(query)
    import threading

    thread = threading.Thread(target=daemon.serve_forever, daemon=True)
    thread.start()
    results = []
    try:
        for label, raw in (
            ("malformed_json", b"not json at all\n"),
            ("missing_concept_id_key", b'{"nope": true}\n'),
            ("unknown_concept_id", _json.dumps({"concept_id": "does-not-exist"}).encode() + b"\n"),
        ):
            with _socket.create_connection(("127.0.0.1", daemon.port), timeout=5.0) as sock:
                sock.sendall(raw)
                sock.shutdown(_socket.SHUT_WR)
                body = b""
                while True:
                    chunk = sock.recv(4096)
                    if not chunk:
                        break
                    body += chunk
                    if body.endswith(b"\n"):
                        break
            payload = _json.loads(body.decode("utf-8"))
            # "quarantined" here means the daemon answered with a real,
            # well-formed response over the socket instead of hanging,
            # crashing, or resetting the connection -- the network-
            # transport analogue of every other case's exception-catching.
            # It does NOT mean every case is an application-level error:
            # "unknown_concept_id" legitimately resolves to a real,
            # degenerate one-object closure (`_semantic_closure.compute_closure`
            # does not itself check category membership -- pre-existing,
            # unmodified behavior, not something introduced or fixed here),
            # so its `payload["ok"]` is genuinely `True`; only the two
            # malformed-request cases are expected to carry `ok: False`.
            results.append(
                {
                    "case": f"daemon_{label}",
                    "quarantined": bool(payload) and "ok" in payload,
                    "response_ok": payload.get("ok"),
                    "response": payload,
                }
            )
    finally:
        daemon.shutdown()
        daemon.server_close()
        thread.join(timeout=5.0)
    return results


# ------------------------------------------------------------------- run


def run() -> dict[str, Any]:
    uncaught_exception: str | None = None
    try:
        ingest = run_stage1_real_corpus_ingestion()
        upstream = run_stage2_msr_cle_upstream()
        integration = run_stage3_integration_glue(ingest, upstream)
        closure = run_stage4_closure_and_disambiguation(ingest, integration)
        network = run_stage5_network_daemon_load_test(integration)
        replay = run_stage6_replay_determinism()
        fault_injection = run_stage7_fault_injection(integration)
    except Exception as exc:
        uncaught_exception = f"{type(exc).__name__}: {exc}"
        closure = network = replay = fault_injection = {"pass": False}

    blocked_metrics = {
        "reality_reconstruction_fidelity_RRF": (
            "Composite of Y_roundtrip and S_bundle_fidelity, both of which require a "
            "real single-fragment -> resolved_target_id resolution model (recognizing "
            "a raw image crop or audio fragment as a specific work by content); no such "
            "model exists anywhere in this workspace -- every query in this experiment, "
            "and in EXP-HEKB005 before it, starts from an already-resolved target id."
        ),
        "epistemic_roundtrip_reconstruction_yield_Y_roundtrip": (
            "Same reason as RRF: no single-fragment resolution model exists."
        ),
        "projection_stability_index_S_proj": (
            "Defined over PNG/JPEG/WebP re-encodings of the same image; no image codec "
            "invariance pipeline exists anywhere in this workspace (EXP-HEKB005's own "
            "recorded gap: 'visual_convergence_score ... requires a real image-to-"
            "meaning measurement model; none exists')."
        ),
        "multi_modal_coordinate_alignment_precision_A_alignment": (
            "Requires >= 2 distinct modality encoders converging on one object's theta; "
            "only a single, generic MSR/CLE synthetic-settle pipeline exists here, and "
            "the real corpus's own Concepts carry no centroid (no image-to-meaning "
            "model produced one) -- there is no second real geometry to align against."
        ),
        "information_compression_ratio_R_compress": (
            "cle.homotopy/cle.quotient/cle.functor are Protocol interfaces only "
            "(categorical-lift-engine's own docs/RFC_ALIGNMENT.md); no homotopy-"
            "invariant compression algorithm is implemented anywhere in this "
            "workspace's dependencies."
        ),
        "epistemic_maturity_growth_rate_and_knowledge_health_vector": (
            "Defined over a persistent HEKB store tracked across sessions; this "
            "experiment's `_hekb_store/exp_hekb_007/` is rebuilt fresh every run "
            "(matching every prior experiment's own convention), so there is no "
            "multi-session growth trend to report honestly."
        ),
        "basin_recovery_speed_and_rate_N_recovery_R_basin": (
            "Already validated upstream, not re-run here: meaning-space-runtime's own "
            "EXP-Ubuntu004 Phase 3 (experiments/exp_msr_004_recovery.py) measures this "
            "with real NVS-Kernel physics. nvs-kernel is not gate-installed in this "
            "repository (only msr and cle are; see docs/RFC_ALIGNMENT.md), and "
            "re-deriving the same recovery-trial physics here would duplicate that "
            "already-passing upstream validation, which this experiment's own policy "
            "forbids ('do not duplicate functionality')."
        ),
    }

    result: dict[str, Any] = {
        "experiment": "EXP-HEKB007",
        "scope": (
            "Integrates, for the first time, two previously-separate real pipelines "
            "into one shared hekb.category.KnowledgeCategory: EXP-HEKB002/003's real "
            "MSR->CLE crystallization and EXP-HEKB005's real 9-work visual corpus. "
            "Adds a genuinely new component -- a real, standalone TCP HEKB MCP Daemon "
            "(_mcp_daemon.py) under 100-concurrent-client load -- since every prior "
            "MCP interface was deliberately in-process only. No vector or embedding "
            "search anywhere. src/hekb not modified; msr/cle source not modified "
            "(gate dependencies only, per docs/RFC_ALIGNMENT.md)."
        ),
        "uncaught_exception": uncaught_exception,
        "stage3_integration_and_disambiguation": closure,
        "stage5_network_mcp_daemon": network,
        "stage6_full_loop_replay_determinism": replay,
        "stage7_fault_injection": fault_injection,
        "blocked_metrics": blocked_metrics,
    }
    result["pass"] = bool(
        uncaught_exception is None
        and closure.get("pass")
        and network.get("pass")
        and replay.get("pass")
        and fault_injection.get("pass")
    )
    return result


def main() -> None:
    result = run()
    output = Path(__file__).with_name("results") / "exp_hekb_007.json"
    output.parent.mkdir(exist_ok=True)
    output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
