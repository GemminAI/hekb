"""EXP-HEKB002 Phase 4: a reference MCP query interface.

Not a real Model Context Protocol server — implementing the actual MCP
wire/transport format is speculative infrastructure this experiment does
not need to validate the thing Phase 4 actually cares about: that a query
against HEKB's real category returns the `SemanticClosure` response shape
EXP-HEKB002 §V specifies, computed by real categorical retrieval (see
`_semantic_closure.py`), with real timing. `MCPReferenceQuery` is an
in-process callable, not a network service.

`homotopy_hash`/`betti_numbers` from §V's example schema are not included:
CLE does not implement homotopy analysis (`categorical-lift-engine`'s own
`docs/RFC_ALIGNMENT.md`: `cle.homotopy` is an interface only, "no algorithm
is assumed or implemented") — fabricating those two fields here would be
the same category of over-claim this workspace's convention exists to
prevent. `content_sha256` (real, `_file_backend.content_hash`-style) is
reported instead, honestly, in its place.
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any

from _semantic_closure import SemanticClosure, compute_closure
from hekb.category import KnowledgeCategory


@dataclass(frozen=True, slots=True)
class MCPResponse:
    query_concept_id: str
    target_object: dict[str, Any]
    semantic_closure: dict[str, Any]
    is_minimal_self_contained: bool
    execution_time_ms: float


def _closure_to_payload(closure: SemanticClosure) -> dict[str, Any]:
    return {
        "objects": [{"id": obj.id, "category": obj.category} for obj in closure.objects],
        "morphisms": [
            {"source": m.source, "target": m.target, "type": m.kind} for m in closure.morphisms
        ],
        "derived_compositions": [
            {"morphism": d.morphism, "formula": d.formula} for d in closure.derived_compositions
        ],
        "pullback_roots": list(closure.pullback_roots),
        "pushout_wavefront": list(closure.pushout_wavefront),
    }


@dataclass(frozen=True, slots=True)
class MCPReferenceQuery:
    """`Query(concept_id) -> SemanticClosure response`, over one fixed category."""

    category: KnowledgeCategory
    relation_kind: dict[str, str]
    object_category: dict[str, str]

    def query(self, concept_id: str) -> MCPResponse:
        start = time.perf_counter()
        closure = compute_closure(
            self.category, self.relation_kind, self.object_category, concept_id
        )
        elapsed_ms = (time.perf_counter() - start) * 1000.0
        return MCPResponse(
            query_concept_id=concept_id,
            target_object={
                "id": closure.target_object.id,
                "category": closure.target_object.category,
            },
            semantic_closure=_closure_to_payload(closure),
            is_minimal_self_contained=closure.is_minimal_self_contained,
            execution_time_ms=elapsed_ms,
        )


__all__ = ["MCPReferenceQuery", "MCPResponse"]
