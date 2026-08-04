"""EXP-HEKB001's own concrete `ProjectionBackend`: a real, file-based store.

Not part of `hekb`'s storage-ignorant core — `src/hekb` never imports this;
the dependency points from here to `hekb`, never the reverse. This is
exactly the extension point `docs/architecture.md` already describes:
*"Concrete backends (relational, columnar, object storage, ...) are out of
scope for v1.0 by design: they belong in a separate package that depends
on HEKB, never the reverse."* This module lives in `experiments/`, the
same status `cle.reference` has in the sibling `categorical-lift-engine`
repository: a validation fixture, not production `hekb` code.

Storage-ignorance note: this module writes plain JSON files via the
standard library only (`json`, `hashlib`, `pathlib`) — no database driver
is imported. `tests/test_storage_ignorance_audit.py` only scans
`src/hekb` anyway, so this module is outside its scope regardless; the
point is made here for the record, not because the audit would catch it.

Fidelity note (see `docs/RFC_ALIGNMENT.md`, "StorageProfile fidelity
gap"): `hekb.storage.to_storage_profile` emits a *declarative* summary of
a morphism (id, domain, codomain, invariants) — it does not include the
morphism's `mapping`, and `HEKBCoreRuntime.ingest_object` never calls the
backend at all, so no `Concept` ever reaches a `ProjectionBackend` today.
This backend persists exactly what it is handed — a `StorageProfile` — and
round-trips *that* faithfully. It does not attempt to reconstruct a full
`Concept`/`KnowledgeRelation` from storage, because the current ABI does
not carry enough information to do so; claiming otherwise would be
validating a capability that does not exist.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from hekb.models import StorageProfile


def _canonical_bytes(profile: StorageProfile) -> bytes:
    """A canonical, deterministic byte encoding of a `StorageProfile`'s content."""
    payload = {
        "storage_class": profile.storage_class,
        "capabilities": dict(sorted(profile.capabilities.items())),
        "payload_snapshot": profile.payload_snapshot,
    }
    return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")


def content_hash(profile: StorageProfile) -> str:
    """A deterministic SHA-256 over a `StorageProfile`'s declared content."""
    return hashlib.sha256(_canonical_bytes(profile)).hexdigest()


def _record_id(profile: StorageProfile) -> str:
    morphism_id = profile.payload_snapshot.get("morphism_id")
    if not isinstance(morphism_id, str) or not morphism_id:
        raise ValueError(
            "FileProjectionBackend requires payload_snapshot['morphism_id'] "
            "(a non-empty str) as the record's storage identity"
        )
    return morphism_id


class FileProjectionBackend:
    """A real `ProjectionBackend`: one JSON file per morphism id, under `root_dir`.

    Deterministic and idempotent by construction — `write` is keyed by the
    profile's own `morphism_id`, so committing the same content twice
    produces one byte-identical file, never a duplicate record.
    """

    def __init__(self, root_dir: Path) -> None:
        self._root = root_dir
        self._root.mkdir(parents=True, exist_ok=True)

    def _path_for(self, record_id: str) -> Path:
        return self._root / f"{record_id}.json"

    def write(self, profile: StorageProfile) -> None:
        record_id = _record_id(profile)
        record: dict[str, Any] = {
            "storage_class": profile.storage_class,
            "capabilities": dict(profile.capabilities),
            "payload_snapshot": profile.payload_snapshot,
            "content_sha256": content_hash(profile),
        }
        self._path_for(record_id).write_text(json.dumps(record, sort_keys=True, indent=2) + "\n")

    def load(self, record_id: str) -> StorageProfile:
        record = json.loads(self._path_for(record_id).read_text())
        profile = StorageProfile(
            storage_class=record["storage_class"],
            capabilities=record["capabilities"],
            payload_snapshot=record["payload_snapshot"],
        )
        if content_hash(profile) != record["content_sha256"]:
            raise ValueError(f"integrity check failed for {record_id!r}: hash mismatch on load")
        return profile

    def replay(self) -> tuple[StorageProfile, ...]:
        """Reconstruct every persisted `StorageProfile` from disk, id-sorted.

        Simulates a process restart: a fresh `FileProjectionBackend` pointed
        at the same `root_dir` and calling only `replay()` sees exactly what
        prior `write` calls (from this process or an earlier one) left
        behind — nothing is cached in this object between calls.
        """
        record_ids = sorted(path.stem for path in self._root.glob("*.json"))
        return tuple(self.load(record_id) for record_id in record_ids)

    @property
    def record_count(self) -> int:
        return sum(1 for _ in self._root.glob("*.json"))


__all__ = ["FileProjectionBackend", "content_hash"]
