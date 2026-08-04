"""EXP-HEKB002 — Closed-Loop End-to-End Verification.

Validates the full loop this specification names: a real, deterministic
`MeaningSpaceRuntime` (standing in for "Local Model -> semantic-annotator-core
-> Meaning Mapper", per the scope decision in `_msr_cle_pipeline.py` and
`docs/RFC_ALIGNMENT.md`) settles into a genuinely novel attractor; a real
`CategoricalLiftEngine` (`categorical-lift-engine`, its own `cle.reference`
strategies) lifts it into a `Concept`; `_cle_hekb_adapter` bridges it into
HEKB's object model (Path A); a deterministic property-graph fixture
standing in for Graphify (`_graphify_reference`, explicitly *not*
production Graphify — see `docs/RFC_ALIGNMENT.md`) is mapped into the same
category via a real Functorial Graph Adapter (Path B); both paths persist
through real, content-hashed file stores (`_file_backend`,
`_concept_store`, both new here and outside `src/hekb`); a Semantic Closure
Engine (`_semantic_closure`, pure categorical retrieval — no vector or
embedding search) answers queries against the merged category; a reference
MCP interface (`_mcp_reference`) wraps that in the response shape
EXP-HEKB002 Section V specifies; and the concept reloaded from disk is fed
back into a *fresh* `msr.field.FieldPrior` via `msr`'s own, unmodified,
already-published `msr.adapters.hekb.field_prior_from_concepts` — proving
the recovered knowledge is functionally reusable, not merely
byte-identical.

`src/hekb` is not modified. `msr`/`cle` source is not modified — both
installed editable into this repository's `.venv` for `experiments/` use
only (see `docs/RFC_ALIGNMENT.md`, "Gate dependency: msr, cle").
"""

from __future__ import annotations

import dataclasses
import json
import shutil
from pathlib import Path
from typing import Any

import numpy as np
from msr.abi import MeaningMeasurement
from msr.adapters.hekb import field_prior_from_concepts
from msr.host import MSRHost
from msr.reference import RecordingKernel
from msr.runtime import MeaningSpaceRuntime

from _cle_hekb_adapter import cle_concept_to_hekb
from _concept_store import FileConceptStore, concept_content_hash
from _file_backend import FileProjectionBackend, content_hash
from _functorial_graph_adapter import check_functoriality, graph_to_hekb
from _graphify_reference import build_property_graph
from _mcp_reference import MCPReferenceQuery
from _msr_cle_pipeline import DIMENSION, FRAME, WELL_MEAN, run_upstream
from _semantic_closure import compute_closure
from hekb.category import CategoryAxiomViolation, KnowledgeCategory
from hekb.models import Concept, KnowledgeRelation
from hekb.runtime import HEKBCoreRuntime
from hekb.storage import to_storage_profile

STORE_ROOT = Path(__file__).with_name("_hekb_store") / "exp_hekb_002"
RELATION_STORE = STORE_ROOT / "relations"
CONCEPT_STORE = STORE_ROOT / "concepts"

GROUNDING_RELATION_ID = "EngineConcept_grounded_in_MeaningMeasurement"
MCP_QUERY_SAMPLES = 200
MCP_LATENCY_TARGET_MS = 5.0

REINJECT_PERTURBATION = np.array([0.9, -0.9])
REINJECT_STEP_BUDGET = 150
REINJECT_DT = 0.1
REINJECT_VARIANCE = 0.05


def _fresh_dir(path: Path) -> Path:
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True)
    return path


@dataclasses.dataclass
class Phase2Result:
    category: KnowledgeCategory
    relation_kind: dict[str, str]
    object_category: dict[str, str]
    engine_concept: Concept
    all_concepts: tuple[Concept, ...]
    all_relations: tuple[KnowledgeRelation, ...]
    concept_backend: FileConceptStore
    relation_backend: FileProjectionBackend


def run_phase1_upstream() -> Any:
    return run_upstream()


def run_phase2_dual_ingestion(upstream: Any) -> Phase2Result:
    concept_root = _fresh_dir(CONCEPT_STORE)
    relation_root = _fresh_dir(RELATION_STORE)
    concept_backend = FileConceptStore(concept_root)
    relation_backend = FileProjectionBackend(relation_root)
    runtime = HEKBCoreRuntime(relation_backend)

    # Path B: Graphify (fixture) -> Functorial Graph Adapter -> HEKB.
    graph = build_property_graph()
    graph_concepts, graph_relations, relation_kind = graph_to_hekb(graph)
    object_category = {node.id: node.category for node in graph.nodes}
    for concept in graph_concepts:
        runtime.ingest_object(concept)
        concept_backend.write(concept)
    for relation in graph_relations:
        runtime.ingest_morphism(relation)

    # Path A: CLE HEKBCommitCandidate -> HEKB.
    cle_candidate = upstream.commit_candidates[0]
    cle_concept = cle_candidate.delta.concept
    assert cle_concept is not None, "expected a Concept-kind candidate from a novel trajectory"
    engine_concept = cle_concept_to_hekb(cle_concept)
    object_category[engine_concept.id] = "CrystallizedKnowledge"
    runtime.ingest_object(engine_concept)
    concept_backend.write(engine_concept)

    # Dual-source cross-reference: the engine concept traces its grounding
    # to the human-authored MeaningMeasurement definition (Path B).
    grounding = KnowledgeRelation(
        id=GROUNDING_RELATION_ID,
        source=engine_concept.id,
        target="MeaningMeasurement",
        mapping={engine_concept.id: "MeaningMeasurement"},
    )
    runtime.ingest_morphism(grounding)
    relation_kind[GROUNDING_RELATION_ID] = "grounded_in"

    all_concepts = (*graph_concepts, engine_concept)
    all_relations = (*graph_relations, grounding)

    return Phase2Result(
        category=runtime.category,
        relation_kind=relation_kind,
        object_category=object_category,
        engine_concept=engine_concept,
        all_concepts=all_concepts,
        all_relations=all_relations,
        concept_backend=concept_backend,
        relation_backend=relation_backend,
    )


def check_persistence(phase2: Phase2Result) -> dict[str, Any]:
    round_trip_ok = True
    for concept in phase2.all_concepts:
        loaded_concept = phase2.concept_backend.load(concept.id)
        if loaded_concept != concept or concept_content_hash(
            loaded_concept
        ) != concept_content_hash(concept):
            round_trip_ok = False
    for relation in phase2.all_relations:
        original_profile = to_storage_profile(relation)
        loaded_profile = phase2.relation_backend.load(relation.id)
        if loaded_profile != original_profile or content_hash(loaded_profile) != content_hash(
            original_profile
        ):
            round_trip_ok = False

    fresh_concepts = FileConceptStore(CONCEPT_STORE).replay()
    fresh_relations = FileProjectionBackend(RELATION_STORE).replay()
    concepts_match = {c.id: c for c in fresh_concepts} == {c.id: c for c in phase2.all_concepts}
    deterministic_replay = concepts_match and {
        p.payload_snapshot["morphism_id"] for p in fresh_relations
    } == {r.id for r in phase2.all_relations}

    sample_concept = phase2.all_concepts[0]
    sample_relation = phase2.all_relations[0]
    before_concept_count = phase2.concept_backend.record_count
    before_relation_count = phase2.relation_backend.record_count
    phase2.concept_backend.write(sample_concept)  # redundant double-commit
    phase2.relation_backend.write(to_storage_profile(sample_relation))
    idempotent = (
        phase2.concept_backend.record_count == before_concept_count
        and phase2.relation_backend.record_count == before_relation_count
    )

    try:
        phase2.category.add_morphism(sample_relation)
        duplicate_rejected = False
    except CategoryAxiomViolation:
        duplicate_rejected = True

    return {
        "round_trip_identity": round_trip_ok,
        "deterministic_replay": deterministic_replay,
        "idempotent_commit": idempotent,
        "duplicate_detection": duplicate_rejected,
        "pass": bool(round_trip_ok and deterministic_replay and idempotent and duplicate_rejected),
    }


def check_dual_source_alignment(phase2: Phase2Result) -> dict[str, Any]:
    grounding = phase2.category.morphism(GROUNDING_RELATION_ID)
    context_edge = phase2.category.morphism("MeaningMeasurement_context_RFC-MM001")
    if grounding.target != context_edge.source:
        return {"composable": False, "pass": False}
    composed = phase2.category.compose(grounding, context_edge)
    expected_mapping = {a: context_edge.mapping[b] for a, b in grounding.mapping.items()}
    correct = (
        composed.source == phase2.engine_concept.id
        and composed.target == "RFC-MM001"
        and composed.mapping == expected_mapping
    )
    return {
        "composable": True,
        "composed_source": composed.source,
        "composed_target": composed.target,
        "pass": bool(correct),
    }


def check_semantic_closure(phase2: Phase2Result) -> dict[str, Any]:
    query_id = phase2.engine_concept.id
    args = (phase2.category, phase2.relation_kind, phase2.object_category, query_id)
    first = compute_closure(*args)
    second = compute_closure(*args)
    deterministic = first == second

    correctness = (
        first.is_minimal_self_contained
        and "MeaningMeasurement" in {o.id for o in first.objects}
        and "RFC-MM001" in set(first.pullback_roots)
        and len(first.derived_compositions) > 0
    )

    functoriality = check_functoriality(
        phase2.category,
        f_edge=_edge_of(phase2, "RFC-MSR01_dependency_MeaningMeasurement"),
        g_edge=_edge_of(phase2, "MeaningMeasurement_context_RFC-MM001"),
    )

    return {
        "deterministic_closure": deterministic,
        "closure_correct": bool(correctness),
        "functoriality_preserved": bool(functoriality),
        "pullback_roots": list(first.pullback_roots),
        "pushout_wavefront": list(first.pushout_wavefront),
        "derived_composition_count": len(first.derived_compositions),
        "pass": bool(deterministic and correctness and functoriality),
    }


def _edge_of(phase2: Phase2Result, relation_id: str) -> Any:
    from _graphify_reference import PropertyGraphEdge

    relation = phase2.category.morphism(relation_id)
    return PropertyGraphEdge(
        id=relation.id,
        source=relation.source,
        target=relation.target,
        kind=phase2.relation_kind[relation_id],
    )


def check_mcp_query(phase2: Phase2Result) -> dict[str, Any]:
    mcp = MCPReferenceQuery(
        category=phase2.category,
        relation_kind=phase2.relation_kind,
        object_category=phase2.object_category,
    )
    query_id = phase2.engine_concept.id
    latencies_ms: list[float] = []
    last_response = None
    for _ in range(MCP_QUERY_SAMPLES):
        last_response = mcp.query(query_id)
        latencies_ms.append(last_response.execution_time_ms)

    latencies_ms.sort()
    p50 = latencies_ms[len(latencies_ms) // 2]
    p99 = latencies_ms[int(len(latencies_ms) * 0.99)]

    assert last_response is not None
    schema_complete = all(
        key in dataclasses.asdict(last_response)
        for key in (
            "query_concept_id",
            "target_object",
            "semantic_closure",
            "is_minimal_self_contained",
            "execution_time_ms",
        )
    )

    return {
        "sample_count": MCP_QUERY_SAMPLES,
        "latency_p50_ms": p50,
        "latency_p99_ms": p99,
        "latency_target_ms": MCP_LATENCY_TARGET_MS,
        "schema_complete": schema_complete,
        "pass": bool(p99 < MCP_LATENCY_TARGET_MS and schema_complete),
    }


def check_closed_loop_reuse(phase2: Phase2Result) -> dict[str, Any]:
    """Reload the engine concept from disk (not the in-memory original) and
    re-inject it into a *fresh* MSR `FieldPrior` via `msr`'s own,
    unmodified `field_prior_from_concepts` -- then prove a perturbed
    observation is pulled back into the recovered basin.

    One initial `ingest()` establishes the perturbed position; recovery
    itself is field-only relaxation (`advance()`, no further measurement
    anchoring the state at the perturbed point) -- the same pattern
    `meaning-space-runtime/experiments/exp_msr_004_recovery.py` uses for
    its own basin-recovery trials.
    """
    reloaded = phase2.concept_backend.load(phase2.engine_concept.id)
    prior = field_prior_from_concepts([reloaded], FRAME, DIMENSION)

    well_present = len(prior.wells) == 1
    if not well_present:
        return {"well_reconstructed": False, "basin_recovered": False, "pass": False}

    start = WELL_MEAN + REINJECT_PERTURBATION
    host = MSRHost(
        runtime=MeaningSpaceRuntime(frame_id=FRAME, dimension=DIMENSION, prior=prior),
        kernel=RecordingKernel(),
    )
    initial = MeaningMeasurement.isotropic(
        "exp-hekb-002-reinject-perturb", FRAME, start.tolist(), REINJECT_VARIANCE, 0
    )
    host.ingest(initial)

    stabilized_basin_id: str | None = None
    for _index in range(1, REINJECT_STEP_BUDGET):
        result = host.advance(REINJECT_DT)
        if result.stabilized is not None:
            stabilized_basin_id = result.stabilized.basin_id
            break

    basin_recovered = stabilized_basin_id == reloaded.id
    return {
        "well_reconstructed": well_present,
        "reconstructed_well_mean": prior.wells[0].mean.tolist() if well_present else None,
        "basin_recovered": basin_recovered,
        "recovered_basin_id": stabilized_basin_id,
        "pass": bool(well_present and basin_recovered),
    }


def run() -> dict[str, Any]:
    uncaught_exception: str | None = None
    try:
        upstream = run_phase1_upstream()
        phase2 = run_phase2_dual_ingestion(upstream)
        persistence = check_persistence(phase2)
        alignment = check_dual_source_alignment(phase2)
        closure = check_semantic_closure(phase2)
        mcp = check_mcp_query(phase2)
        reuse = check_closed_loop_reuse(phase2)
    except Exception as exc:
        uncaught_exception = f"{type(exc).__name__}: {exc}"
        persistence = alignment = closure = mcp = reuse = {"pass": False}

    end_to_end_yield = uncaught_exception is None

    result: dict[str, Any] = {
        "experiment": "EXP-HEKB002",
        "scope": (
            "Real msr + real cle (installed editable, experiments-only; see "
            "docs/RFC_ALIGNMENT.md) produce one genuine StabilizedTrajectory "
            "-> Concept. Graphify is a deterministic fixture, not production "
            "Graphify (none exists in this workspace). MCP is an in-process "
            "reference query interface, not a real network MCP server. "
            "homotopy_hash/betti_numbers from the spec's example schema are "
            "omitted, not fabricated -- CLE implements no homotopy algorithm."
        ),
        "end_to_end_yield": end_to_end_yield,
        "uncaught_exception": uncaught_exception,
        "persistence": persistence,
        "dual_source_alignment": alignment,
        "semantic_closure": closure,
        "mcp_query": mcp,
        "closed_loop_reuse": reuse,
    }
    result["pass"] = bool(
        end_to_end_yield
        and persistence.get("pass")
        and alignment.get("pass")
        and closure.get("pass")
        and mcp.get("pass")
        and reuse.get("pass")
    )
    return result


def main() -> None:
    result = run()
    output = Path(__file__).with_name("results") / "exp_hekb_002.json"
    output.parent.mkdir(exist_ok=True)
    output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
