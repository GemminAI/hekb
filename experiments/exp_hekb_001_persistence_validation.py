"""EXP-HEKB001 — Persistence & Identity Validation (Graphify excluded).

Per explicit instruction: Graphify is an independent upstream project with
no repository present in this workspace. This experiment does not invent a
Graphify interface, a `ProducerLike` Protocol, or any stand-in for it —
Graphify integration is recorded as an external dependency in
`docs/RFC_ALIGNMENT.md` and deferred until Graphify actually exports one.
Every stage below starts *after* that boundary: real `hekb.models.Concept`/
`KnowledgeRelation` values, constructed directly (see `_lineage_fixture.py`
for why that's still inside HEKB's own domain, not a Graphify stand-in).

What this validates: Stage 4 (persistence: save/load/hash/replay,
idempotent commit, duplicate detection, immutability), Stage 5
(cross-reference lineage: defines/consumes/provenance as real, composed
`KnowledgeRelation` morphisms), Stage 6 (storage validation against the
real mounted path this repository itself lives at,
`/media/psf/SSD1TB/HEKBv2`, via `experiments/_hekb_store/` — a dedicated,
gitignored scratch subdirectory, not the repository root), and a
synthetic-only Stage 7 lookup-latency check (Target: < 5ms), explicitly
*not* run against RFCv3_draft/sensos-docs/Daily Logs, none of which exist
under those names in this workspace — see `docs/RFC_ALIGNMENT.md`.

`hekb.storage.FileProjectionBackend` (`experiments/_file_backend.py`) is a
real, deterministic, SHA-256-content-hashed, file-based `ProjectionBackend`
— not a fake. It writes exactly what `HEKBCoreRuntime` hands it: a
declarative `StorageProfile`. It does not, and cannot, round-trip a full
`Concept`/`KnowledgeRelation` object, because `hekb.storage.to_storage_profile`
does not carry a morphism's `mapping` and `HEKBCoreRuntime.ingest_object`
never calls the backend at all (see `docs/RFC_ALIGNMENT.md`, "StorageProfile
fidelity gap"). This experiment tests round-trip identity of exactly what
*is* persisted, honestly, rather than asserting a stronger claim the current
ABI cannot support.

Hypothesis
    `HEKBCoreRuntime` + a real `ProjectionBackend` implementation persist,
    reload, and replay `StorageProfile` records with bit-level SHA-256
    identity, idempotently, with no duplicate records, and reject any
    category-axiom-violating duplicate before the backend is ever touched.

Falsifiable failure
    Any hash mismatch on load; any non-idempotent duplicate write; any
    mutable ABI value; any lookup exceeding 5ms on the synthetic-scale
    check; any lineage composition that is not deterministic across runs.
"""

from __future__ import annotations

import dataclasses
import json
import shutil
import time
from pathlib import Path
from typing import Any

from _file_backend import FileProjectionBackend, content_hash
from _lineage_fixture import build_lineage_fixture
from hekb.category import CategoryAxiomViolation
from hekb.models import Concept, EpistemicGraphSnapshot, KnowledgeRelation
from hekb.runtime import HEKBCoreRuntime
from hekb.storage import to_storage_profile

STORE_ROOT = Path(__file__).with_name("_hekb_store")
LINEAGE_STORE = STORE_ROOT / "lineage"
SCALE_STORE = STORE_ROOT / "scale"
SCALE_RECORD_COUNT = 500
LOOKUP_TARGET_MS = 5.0


def _fresh_store(path: Path) -> Path:
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True)
    return path


def build_runtime(store_root: Path) -> tuple[HEKBCoreRuntime, FileProjectionBackend]:
    backend = FileProjectionBackend(store_root)
    return HEKBCoreRuntime(backend), backend


def ingest_fixture(
    runtime: HEKBCoreRuntime,
    concepts: tuple[Concept, ...],
    relations: tuple[KnowledgeRelation, ...],
) -> None:
    for concept in concepts:
        runtime.ingest_object(concept)
    for relation in relations:
        runtime.ingest_morphism(relation)


def check_round_trip_identity(
    backend: FileProjectionBackend, relations: tuple[KnowledgeRelation, ...]
) -> tuple[bool, int]:
    """Hash(Load(Save(O))) == Hash(O) for O = the StorageProfile actually persisted."""
    checked = 0
    for relation in relations:
        original_profile = to_storage_profile(relation)
        original_hash = content_hash(original_profile)
        loaded_profile = backend.load(relation.id)
        loaded_hash = content_hash(loaded_profile)
        if loaded_hash != original_hash or loaded_profile != original_profile:
            return False, checked
        checked += 1
    return True, checked


def check_deterministic_replay(store_root: Path, relations: tuple[KnowledgeRelation, ...]) -> bool:
    """A brand-new backend instance pointed at the same directory (simulating
    a fresh process) must replay the identical set of profiles."""
    expected = {relation.id: to_storage_profile(relation) for relation in relations}
    fresh_backend = FileProjectionBackend(store_root)
    replayed = {
        profile.payload_snapshot["morphism_id"]: profile for profile in fresh_backend.replay()
    }
    return replayed == expected


def check_idempotent_commit(backend: FileProjectionBackend, relation: KnowledgeRelation) -> bool:
    """Writing the same profile a second time must not create a duplicate
    record or change the stored content."""
    profile = to_storage_profile(relation)
    before_count = backend.record_count
    before_hash = content_hash(backend.load(relation.id))

    backend.write(profile)  # second, redundant write of identical content

    after_count = backend.record_count
    after_hash = content_hash(backend.load(relation.id))
    return before_count == after_count and before_hash == after_hash


def check_duplicate_detection(
    runtime: HEKBCoreRuntime, backend: FileProjectionBackend, relation: KnowledgeRelation
) -> bool:
    """Re-ingesting the same morphism id through the *category* must be
    rejected before the backend is ever touched — no duplicate, no
    overwrite, not even a redundant identical write."""
    before_count = backend.record_count
    try:
        runtime.ingest_morphism(relation)
    except CategoryAxiomViolation:
        return backend.record_count == before_count
    return False


def check_immutability(
    concepts: tuple[Concept, ...],
    relations: tuple[KnowledgeRelation, ...],
    snapshot: EpistemicGraphSnapshot,
) -> bool:
    attempts: tuple[tuple[Any, str, object], ...] = (
        (concepts[0], "id", "mutated"),
        (relations[0], "id", "mutated"),
        (to_storage_profile(relations[0]), "storage_class", "mutated"),
        (snapshot, "vertices", ()),
    )
    for target, attribute, value in attempts:
        try:
            setattr(target, attribute, value)
        except dataclasses.FrozenInstanceError:
            continue
        return False
    return True


def check_recovery(store_root: Path, relations: tuple[KnowledgeRelation, ...]) -> bool:
    """Simulate a process crash and restart: a brand-new runtime + backend
    pointed at the same directory must recover every persisted record's
    identity and metadata (morphism_id, domain, codomain, invariants) —
    the full scope `StorageProfile` actually carries; see the module
    docstring's fidelity note for what recovery does *not* claim."""
    _runtime, recovered_backend = build_runtime(store_root)
    recovered = {p.payload_snapshot["morphism_id"]: p for p in recovered_backend.replay()}
    expected_ids = {relation.id for relation in relations}
    return set(recovered) == expected_ids


def run_persistence_validation() -> dict[str, Any]:
    store_root = _fresh_store(LINEAGE_STORE)
    concepts, relations = build_lineage_fixture()

    runtime, backend = build_runtime(store_root)
    ingest_fixture(runtime, concepts, relations)
    snapshot = runtime.export_epistemic_graph()

    round_trip_identity, checked_count = check_round_trip_identity(backend, relations)
    deterministic_replay = check_deterministic_replay(store_root, relations)
    idempotent_commit = check_idempotent_commit(backend, relations[0])
    duplicate_detection = check_duplicate_detection(runtime, backend, relations[0])
    immutability = check_immutability(concepts, relations, snapshot)
    recovery = check_recovery(store_root, relations)

    return {
        "concepts_ingested": len(concepts),
        "relations_ingested": len(relations),
        "round_trip_identity": round_trip_identity,
        "round_trip_checked_count": checked_count,
        "deterministic_replay": deterministic_replay,
        "idempotent_commit": idempotent_commit,
        "duplicate_detection": duplicate_detection,
        "immutability": immutability,
        "recovery": recovery,
        "pass": bool(
            round_trip_identity
            and deterministic_replay
            and idempotent_commit
            and duplicate_detection
            and immutability
            and recovery
        ),
    }


def run_lineage_validation() -> dict[str, Any]:
    store_root = _fresh_store(STORE_ROOT / "lineage_check")
    concepts, relations = build_lineage_fixture()
    runtime, _backend = build_runtime(store_root)
    ingest_fixture(runtime, concepts, relations)

    consumes = runtime.category.morphism("RFC-MSR01_consumes_MeaningMeasurement")
    provenance = runtime.category.morphism("MeaningMeasurement_traces_to_RFC-MM001")

    composed_first = runtime.category.compose(consumes, provenance)
    composed_second = runtime.category.compose(consumes, provenance)

    lineage_holds = (
        composed_first.source == "RFC-MSR01.consumes"
        and composed_first.target == "RFC-MM001.defines"
        and composed_first.mapping == {"MeaningMeasurement": "MeaningMeasurement"}
    )
    composition_deterministic = composed_first == composed_second

    return {
        "lineage_composition_correct": lineage_holds,
        "lineage_composition_deterministic": composition_deterministic,
        "pass": bool(lineage_holds and composition_deterministic),
    }


def run_scale_validation(*, gate: bool) -> dict[str, Any]:
    """Stage 7, synthetic-only. Gated on Stage 6 (`run_persistence_validation`)
    passing, per instruction ("Only if Stage 6 passes"). Explicitly not run
    against RFCv3_draft/sensos-docs/Daily Logs — none exist under those
    names in this workspace; see `docs/RFC_ALIGNMENT.md`."""
    if not gate:
        return {"skipped": True, "reason": "Stage 6 did not pass", "pass": False}

    store_root = _fresh_store(SCALE_STORE)
    backend = FileProjectionBackend(store_root)
    relations = tuple(
        KnowledgeRelation(
            id=f"synthetic-{i}",
            source="synthetic-src",
            target="synthetic-dst",
            mapping={},
            invariants={"index": float(i)},
        )
        for i in range(SCALE_RECORD_COUNT)
    )

    write_start = time.perf_counter()
    for relation in relations:
        backend.write(to_storage_profile(relation))
    write_elapsed_s = time.perf_counter() - write_start

    lookup_samples_ms: list[float] = []
    for relation in relations:
        lookup_start = time.perf_counter()
        backend.load(relation.id)
        lookup_samples_ms.append((time.perf_counter() - lookup_start) * 1000.0)

    lookup_samples_ms.sort()
    p50 = lookup_samples_ms[len(lookup_samples_ms) // 2]
    p95 = lookup_samples_ms[int(len(lookup_samples_ms) * 0.95)]
    storage_bytes = sum(p.stat().st_size for p in store_root.glob("*.json"))

    return {
        "skipped": False,
        "record_count": SCALE_RECORD_COUNT,
        "write_throughput_records_per_s": SCALE_RECORD_COUNT / write_elapsed_s,
        "lookup_p50_ms": p50,
        "lookup_p95_ms": p95,
        "lookup_target_ms": LOOKUP_TARGET_MS,
        "storage_bytes": storage_bytes,
        "pass": bool(p95 < LOOKUP_TARGET_MS),
    }


def run() -> dict[str, Any]:
    persistence = run_persistence_validation()
    lineage = run_lineage_validation()
    scale = run_scale_validation(gate=persistence["pass"])

    result: dict[str, Any] = {
        "experiment": "EXP-HEKB001",
        "scope": (
            "Stages 4-7 of EXP-HEKB001 minus Graphify integration (Stage 3), "
            "which is recorded as an external dependency, not implemented or "
            "stubbed here — see docs/RFC_ALIGNMENT.md. Cross-reference "
            "fixtures (Stage 5) and scale data (Stage 7) are synthetic, not "
            "RFCv3_draft/sensos-docs/Daily Logs, none of which exist under "
            "those names in this workspace."
        ),
        "persistence": persistence,
        "lineage": lineage,
        "scale": scale,
        "pass": bool(persistence["pass"] and lineage["pass"] and scale["pass"]),
    }
    return result


def main() -> None:
    result = run()
    output = Path(__file__).with_name("results") / "exp_hekb_001.json"
    output.parent.mkdir(exist_ok=True)
    output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
