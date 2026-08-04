"""EXP-HEKB002's Concept persistence: the gap `hekb.storage` leaves open.

`HEKBCoreRuntime.ingest_object` never calls a `ProjectionBackend` at all
(see `docs/RFC_ALIGNMENT.md`, "StorageProfile fidelity gap" — recorded
during EXP-HEKB001, unmodified since). Metric 2 of EXP-HEKB002
(`Hash(MCP_Query(Save(T))) == Hash(T)`) needs `Concept`s — not just
`KnowledgeRelation`-derived `StorageProfile`s — to actually round-trip
through storage. Rather than adding a second write path to
`HEKBCoreRuntime` (a real behavioral change to production code this
experiment was explicitly told not to make unless genuinely required, and
persisting objects a caller chooses not to persist is not this
experiment's call to make on HEKB's behalf), this module gives the
*harness* its own content-hashed, file-based `Concept` store, in the same
style as `_file_backend.FileProjectionBackend` and living beside it.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from hekb.models import Concept


def _canonical_bytes(concept: Concept) -> bytes:
    payload = {
        "id": concept.id,
        "elements": sorted(concept.elements),
        "centroid": list(concept.centroid) if concept.centroid is not None else None,
        "hessian": (
            [list(row) for row in concept.hessian] if concept.hessian is not None else None
        ),
        "invariants": dict(sorted(concept.invariants.items())),
    }
    return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")


def concept_content_hash(concept: Concept) -> str:
    """A deterministic SHA-256 over a `Concept`'s full content."""
    return hashlib.sha256(_canonical_bytes(concept)).hexdigest()


class FileConceptStore:
    """One JSON file per `Concept.id`, under `root_dir`. Real, deterministic,
    idempotent — mirrors `_file_backend.FileProjectionBackend` exactly."""

    def __init__(self, root_dir: Path) -> None:
        self._root = root_dir
        self._root.mkdir(parents=True, exist_ok=True)

    def _path_for(self, concept_id: str) -> Path:
        return self._root / f"{concept_id}.json"

    def write(self, concept: Concept) -> None:
        record: dict[str, Any] = {
            "id": concept.id,
            "elements": sorted(concept.elements),
            "centroid": list(concept.centroid) if concept.centroid is not None else None,
            "hessian": (
                [list(row) for row in concept.hessian] if concept.hessian is not None else None
            ),
            "invariants": dict(concept.invariants),
            "content_sha256": concept_content_hash(concept),
        }
        self._path_for(concept.id).write_text(json.dumps(record, sort_keys=True, indent=2) + "\n")

    def load(self, concept_id: str) -> Concept:
        record = json.loads(self._path_for(concept_id).read_text())
        concept = Concept(
            id=record["id"],
            elements=frozenset(record["elements"]),
            centroid=(tuple(record["centroid"]) if record["centroid"] is not None else None),
            hessian=(
                tuple(tuple(row) for row in record["hessian"])
                if record["hessian"] is not None
                else None
            ),
            invariants=record["invariants"],
        )
        if concept_content_hash(concept) != record["content_sha256"]:
            raise ValueError(f"integrity check failed for {concept_id!r}: hash mismatch on load")
        return concept

    def replay(self) -> tuple[Concept, ...]:
        concept_ids = sorted(path.stem for path in self._root.glob("*.json"))
        return tuple(self.load(concept_id) for concept_id in concept_ids)

    @property
    def record_count(self) -> int:
        return sum(1 for _ in self._root.glob("*.json"))


__all__ = ["FileConceptStore", "concept_content_hash"]
