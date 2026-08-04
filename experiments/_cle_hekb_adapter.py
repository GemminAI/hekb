"""EXP-HEKB002 Path A: `cle.abi.outputs.Concept` -> `hekb.models.Concept`.

No production adapter exists anywhere in the workspace between CLE's
output ABI and HEKB's object model — they are structurally different by
design: CLE's `Concept` is a point in a continuous meaning space
(`centroid`/`hessian`/`invariants`), HEKB's `Concept` is an object of the
category of finite sets (`elements: frozenset[str]`). This module is the
small, honest bridge Phase 2's "Engine Knowledge Flow" needs, living in
`experiments/` (not `src/hekb`, not `src/cle`) exactly as
`categorical-lift-engine`'s own `docs/RFC_ALIGNMENT.md` already anticipates:
*"a `Concept` this repository eventually commits into HEKB can, once
round-tripped, become a field-prior well for MSR again — without either
repository importing the other."*

**The geometric fields transfer exactly, non-lossy**: both `Concept.centroid`
and `Concept.hessian` are `tuple[float, ...]`/`tuple[tuple[float, ...], ...]`
in both ABIs, and both are shaped to satisfy
`msr.adapters.hekb.ConceptLike` by construction — this is what makes Phase 5
(closed-loop re-injection) possible without a second adapter.

**The `elements` field is genuinely invented here, not extracted**: CLE's
`Concept` has no finite-set structure to carry over. `elements =
frozenset({concept.id})` — a canonical singleton — is the simplest
choice that satisfies HEKB's category axioms (every object needs a
non-empty element set) without fabricating structure CLE never claimed.
"""

from __future__ import annotations

from cle.abi.outputs import Concept as CLEConcept

from hekb.models import Concept as HEKBConcept


def cle_concept_to_hekb(concept: CLEConcept) -> HEKBConcept:
    """A CLE `Concept` -> a HEKB `Concept`, carrying geometry through exactly."""
    return HEKBConcept(
        id=concept.id,
        elements=frozenset({concept.id}),
        centroid=concept.centroid,
        hessian=concept.hessian,
        invariants=dict(concept.invariants),
    )


__all__ = ["cle_concept_to_hekb"]
