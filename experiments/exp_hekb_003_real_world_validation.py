"""EXP-HEKB003 — Real-World Cross-Domain Semantic Search & Closure Validation.

Builds on EXP-HEKB001 (persistence) and EXP-HEKB002 (closed-loop
validation, dual-source ingestion, Semantic Closure Engine) without
redesigning any of them. The one thing this experiment adds that neither
predecessor had: **real** multi-repository artifacts — real Markdown
(`RFC-MSR01.md`, `docs/RFC_ALIGNMENT.md`, `docs/ARCHITECTURE.md`,
`docs/BOUNDARIES.md` across `meaning-space-runtime`, `categorical-lift-engine`,
and this repository), real Python (`ast.parse`-extracted top-level classes
across a curated set of real source files), and real Git history (`git
log` against real commits) — see `_real_corpus.py` for the exact file
list (Stage 1's repository survey) and `_real_artifact_extractors.py` for
how each modality is read. No Graphify repository exists in this
workspace; these are reference extractors, not Graphify, per explicit
instruction.

The "Engine Knowledge" side reuses EXP-HEKB002's real pipeline verbatim
(`_msr_cle_pipeline.run_upstream`, `_cle_hekb_adapter.cle_concept_to_hekb`)
— one real `MeaningSpaceRuntime` + `CategoricalLiftEngine` run, not a
fixture.

`src/hekb` is not modified. No vector or embedding search anywhere —
`_semantic_search.py` is pure categorical retrieval, per explicit
instruction.
"""

from __future__ import annotations

import ast
import dataclasses
import json
import shutil
import subprocess
from pathlib import Path
from typing import Any

from _cle_hekb_adapter import cle_concept_to_hekb
from _concept_store import FileConceptStore
from _file_backend import FileProjectionBackend
from _functorial_graph_adapter import graph_to_hekb
from _msr_cle_pipeline import run_upstream
from _real_corpus import MSR_ROOT, build_real_property_graph
from _semantic_search import search, search_result_payload
from hekb.category import KnowledgeCategory
from hekb.runtime import HEKBCoreRuntime

STORE_ROOT = Path(__file__).with_name("_hekb_store") / "exp_hekb_003"
RELATION_STORE = STORE_ROOT / "relations"
CONCEPT_STORE = STORE_ROOT / "concepts"

SCALE_QUERY_SAMPLES = 100
LATENCY_TARGET_MS = 10.0
GROUNDING_TARGET_ID = "MeaningMeasurement"


def _fresh_dir(path: Path) -> Path:
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True)
    return path


@dataclasses.dataclass
class Corpus2Result:
    category: KnowledgeCategory
    relation_kind: dict[str, str]
    object_category: dict[str, str]
    engine_concept_id: str
    concept_backend: FileConceptStore
    relation_backend: FileProjectionBackend


def run_stage1_survey() -> dict[str, Any]:
    _graph, survey = build_real_property_graph()
    return survey.as_dict()


def run_stage2_3_ingestion() -> Corpus2Result:
    concept_root = _fresh_dir(CONCEPT_STORE)
    relation_root = _fresh_dir(RELATION_STORE)
    concept_backend = FileConceptStore(concept_root)
    relation_backend = FileProjectionBackend(relation_root)
    runtime = HEKBCoreRuntime(relation_backend)

    graph, _survey = build_real_property_graph()
    concepts, relations, relation_kind = graph_to_hekb(graph)
    object_category = {node.id: node.category for node in graph.nodes}

    for concept in concepts:
        runtime.ingest_object(concept)
        concept_backend.write(concept)
    for relation in relations:
        runtime.ingest_morphism(relation)

    # Engine Knowledge side: EXP-HEKB002's real pipeline, reused verbatim.
    upstream = run_upstream()
    cle_concept = upstream.commit_candidates[0].delta.concept
    assert cle_concept is not None
    engine_concept = cle_concept_to_hekb(cle_concept)
    object_category[engine_concept.id] = "CrystallizedKnowledge"
    runtime.ingest_object(engine_concept)
    concept_backend.write(engine_concept)

    grounding_id = f"{engine_concept.id}_depends_on_{GROUNDING_TARGET_ID}"
    from hekb.models import KnowledgeRelation

    grounding = KnowledgeRelation(
        id=grounding_id,
        source=engine_concept.id,
        target=GROUNDING_TARGET_ID,
        mapping={engine_concept.id: GROUNDING_TARGET_ID},
    )
    runtime.ingest_morphism(grounding)
    relation_kind[grounding_id] = "depends_on"

    return Corpus2Result(
        category=runtime.category,
        relation_kind=relation_kind,
        object_category=object_category,
        engine_concept_id=engine_concept.id,
        concept_backend=concept_backend,
        relation_backend=relation_backend,
    )


def run_stage4_5_searches(corpus: Corpus2Result) -> dict[str, Any]:
    queries = (
        GROUNDING_TARGET_ID,  # dual-source: human RFC + engine concept both connect here
        "msr/docs/BOUNDARIES.md",  # real depth->=4 composition chain
        corpus.engine_concept_id,  # engine-discovered concept's own closure
    )
    results: dict[str, Any] = {}
    exceptions: list[str] = []
    for query in queries:
        try:
            result = search(query, corpus.category, corpus.relation_kind, corpus.object_category)
            if result is None:
                exceptions.append(f"{query}: concept resolution failed")
                continue
            results[query] = search_result_payload(result)
        except Exception as exc:
            exceptions.append(f"{query}: {type(exc).__name__}: {exc}")

    cross_domain_yield = len(exceptions) == 0

    max_depth = max((r["search_metrics"]["composition_depth"] for r in results.values()), default=0)

    return {
        "queries": list(queries),
        "exceptions": exceptions,
        "cross_domain_traversal_yield": cross_domain_yield,
        "max_composition_depth": max_depth,
        "results": results,
        "pass": bool(cross_domain_yield and max_depth >= 4),
    }


def check_deterministic_replay(corpus: Corpus2Result) -> dict[str, Any]:
    def _normalized(query: str) -> dict[str, Any] | None:
        result = search(query, corpus.category, corpus.relation_kind, corpus.object_category)
        if result is None:
            return None
        payload = search_result_payload(result)
        payload["search_metrics"].pop("execution_time_ms")
        return payload

    query = GROUNDING_TARGET_ID
    first = _normalized(query)
    second = _normalized(query)
    return {"deterministic": first == second, "pass": bool(first == second)}


def check_pullback_accuracy(corpus: Corpus2Result) -> dict[str, Any]:
    """Independent check: `msr/src/msr/abi.py` (real code) and
    `msr/docs/RFC_ALIGNMENT.md` (real spec) both real-reference
    `MeaningMeasurement` -- re-verified here by grepping their real raw
    text directly, not by trusting the closure algorithm's own output."""
    abi_text = (MSR_ROOT / "src/msr/abi.py").read_text()
    alignment_text = (MSR_ROOT / "docs/RFC_ALIGNMENT.md").read_text()
    independently_confirmed = "MeaningMeasurement" in abi_text and (
        "MeaningMeasurement" in alignment_text or "msr.abi" in alignment_text
    )

    code_result = search(
        "msr/src/msr/abi.py", corpus.category, corpus.relation_kind, corpus.object_category
    )
    assert code_result is not None
    shared_root_found = GROUNDING_TARGET_ID in code_result.closure.pullback_roots

    return {
        "independently_confirmed_in_source": independently_confirmed,
        "shared_pullback_root_found": shared_root_found,
        "pass": bool(independently_confirmed and shared_root_found),
    }


def check_pushout_recall(corpus: Corpus2Result) -> dict[str, Any]:
    """Independent check: re-scan the real property graph from scratch for
    every edge whose target is `MeaningMeasurement`, and verify every one
    of those real sources appears in the closure -- not merely trusted
    because the closure algorithm included it."""
    graph, _survey = build_real_property_graph()
    expected_direct_dependents = {
        edge.source for edge in graph.edges if edge.target == GROUNDING_TARGET_ID
    }

    result = search(
        GROUNDING_TARGET_ID, corpus.category, corpus.relation_kind, corpus.object_category
    )
    assert result is not None
    closure_object_ids = {obj.id for obj in result.closure.objects}

    missing = expected_direct_dependents - closure_object_ids
    recall = (
        1.0
        if not expected_direct_dependents
        else 1.0 - len(missing) / len(expected_direct_dependents)
    )
    return {
        "expected_direct_dependent_count": len(expected_direct_dependents),
        "missing": sorted(missing),
        "recall": recall,
        "pass": bool(recall == 1.0),
    }


def check_latency_at_scale(corpus: Corpus2Result) -> dict[str, Any]:
    latencies_ms: list[float] = []
    for _ in range(SCALE_QUERY_SAMPLES):
        result = search(
            GROUNDING_TARGET_ID, corpus.category, corpus.relation_kind, corpus.object_category
        )
        assert result is not None
        latencies_ms.append(result.execution_time_ms)
    latencies_ms.sort()
    p50 = latencies_ms[len(latencies_ms) // 2]
    p99 = latencies_ms[int(len(latencies_ms) * 0.99)]
    return {
        "sample_count": SCALE_QUERY_SAMPLES,
        "node_count": len(corpus.category.objects),
        "latency_p50_ms": p50,
        "latency_p99_ms": p99,
        "latency_target_ms": LATENCY_TARGET_MS,
        "pass": bool(p99 < LATENCY_TARGET_MS),
    }


def _real_classes_at_revision(rev: str) -> tuple[str, ...]:
    """Real top-level class names in `msr/src/msr/abi.py` as of a real git
    revision -- `git show` + `ast.parse`, not a synthetic diff."""
    content = subprocess.run(
        ["git", "show", f"{rev}:src/msr/abi.py"],
        cwd=MSR_ROOT,
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    tree = ast.parse(content, filename=f"abi.py@{rev[:7]}")
    return tuple(node.name for node in ast.iter_child_nodes(tree) if isinstance(node, ast.ClassDef))


def check_differential_synchronization() -> dict[str, Any]:
    """Real `git diff` re-synchronization: two real revisions of
    `msr/src/msr/abi.py`, each re-extracted independently (`git show` +
    `ast.parse`) and ingested into a fresh category as
    `msr/src/msr/abi.py@<rev>` -- one node per revision, since a
    revision's structure is a distinct historical fact, not
    interchangeable with another revision's. Re-ingesting the *same*
    revision a second time must add nothing (idempotent, 0-duplication)."""
    log = subprocess.run(
        ["git", "log", "--max-count=2", "--format=%H", "--", "src/msr/abi.py"],
        cwd=MSR_ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    revisions = [line.strip() for line in log.stdout.splitlines() if line.strip()]
    if len(revisions) < 2:
        return {"skipped": True, "reason": "fewer than 2 real revisions available", "pass": False}

    root = _fresh_dir(STORE_ROOT / "diff_sync")
    backend = FileProjectionBackend(root)
    runtime = HEKBCoreRuntime(backend)

    import contextlib

    from hekb.category import CategoryAxiomViolation
    from hekb.models import Concept, KnowledgeRelation

    def _ingest_revision(rev: str) -> int:
        classes = _real_classes_at_revision(rev)
        file_node_id = f"msr/src/msr/abi.py@{rev[:7]}"
        # idempotent: this revision's node already exists on a re-ingest
        with contextlib.suppress(CategoryAxiomViolation):
            runtime.ingest_object(Concept(id=file_node_id, elements=frozenset({file_node_id})))
        new_relations = 0
        for class_name in classes:
            # idempotent: concept shared across revisions
            with contextlib.suppress(CategoryAxiomViolation):
                runtime.ingest_object(Concept(id=class_name, elements=frozenset({class_name})))
            relation = KnowledgeRelation(
                id=f"{file_node_id}_implements_{class_name}",
                source=file_node_id,
                target=class_name,
                mapping={file_node_id: class_name},
            )
            try:
                runtime.ingest_morphism(relation)
                new_relations += 1
            except CategoryAxiomViolation:
                pass  # idempotent: identical morphism id already present
        return new_relations

    before_count = backend.record_count
    first_new = _ingest_revision(revisions[0])
    after_first = backend.record_count
    second_new = _ingest_revision(revisions[0])  # re-ingest same revision: must be 0-duplication
    after_second = backend.record_count
    other_new = _ingest_revision(revisions[1])  # a genuinely different real revision

    idempotent = after_first == after_second and second_new == 0
    diff_identity = after_first == before_count + first_new

    return {
        "revisions_compared": revisions,
        "first_ingest_new_relations": first_new,
        "second_ingest_new_relations": second_new,
        "other_revision_new_relations": other_new,
        "idempotent": idempotent,
        "diff_identity": diff_identity,
        "pass": bool(idempotent and diff_identity),
    }


def run() -> dict[str, Any]:
    uncaught_exception: str | None = None
    try:
        survey = run_stage1_survey()
        corpus = run_stage2_3_ingestion()
        stage4_5 = run_stage4_5_searches(corpus)
        replay = check_deterministic_replay(corpus)
        pullback = check_pullback_accuracy(corpus)
        pushout = check_pushout_recall(corpus)
        latency = check_latency_at_scale(corpus)
        diff_sync = check_differential_synchronization()
    except Exception as exc:
        uncaught_exception = f"{type(exc).__name__}: {exc}"
        survey = {}
        stage4_5 = replay = pullback = pushout = latency = diff_sync = {"pass": False}

    result: dict[str, Any] = {
        "experiment": "EXP-HEKB003",
        "scope": (
            "Real multi-repository artifacts (meaning-space-runtime, "
            "categorical-lift-engine, this repository): real Markdown, real "
            "Python (ast.parse), real git log. Graphify does not exist in "
            "this workspace -- _real_artifact_extractors.py are reference "
            "extractors, not Graphify. No vector/embedding search anywhere."
        ),
        "uncaught_exception": uncaught_exception,
        "stage1_survey": survey,
        "stage4_5_searches": stage4_5,
        "deterministic_replay": replay,
        "pullback_accuracy": pullback,
        "pushout_recall": pushout,
        "latency_at_scale": latency,
        "differential_synchronization": diff_sync,
    }
    result["pass"] = bool(
        uncaught_exception is None
        and stage4_5.get("pass")
        and replay.get("pass")
        and pullback.get("pass")
        and pushout.get("pass")
        and latency.get("pass")
        and diff_sync.get("pass")
    )
    return result


def main() -> None:
    result = run()
    output = Path(__file__).with_name("results") / "exp_hekb_003.json"
    output.parent.mkdir(exist_ok=True)
    output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
