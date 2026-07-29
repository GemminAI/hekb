"""hekb: the HEKB algebraic core.

A storage-ignorant, category-theoretic knowledge substrate: K (the
knowledge category) is modeled concretely as the category of finite sets
and functions, giving category axioms, the Homotopic Update Law, pushouts
and pullbacks as universal problems, and the tensor/internal-hom
adjunction each a real, constructive, checkable implementation. See
``README.md`` for the full design philosophy and quick start.
"""

from hekb.category import (
    CategoryAxiomViolation,
    HomotopyViolation,
    KnowledgeCategory,
    compose_all,
    decode_function,
    decode_pair,
    encode_function,
    encode_pair,
)
from hekb.models import Concept, EpistemicGraphSnapshot, KnowledgeRelation, StorageProfile
from hekb.runtime import HEKBCoreRuntime
from hekb.storage import InMemoryProjectionBackend, ProjectionBackend, to_storage_profile


def main() -> None:
    """Minimal standalone demo entry point (no CLI/transport defined yet)."""
    runtime = HEKBCoreRuntime(InMemoryProjectionBackend())
    print(
        "hekb: HEKB Algebraic Core — standalone demo. "
        "See README.md for usage; this package is a library, not a service, "
        "until a transport is defined in a later phase."
    )
    print(runtime.export_epistemic_graph())


__all__ = [
    "CategoryAxiomViolation",
    "Concept",
    "EpistemicGraphSnapshot",
    "HEKBCoreRuntime",
    "HomotopyViolation",
    "InMemoryProjectionBackend",
    "KnowledgeCategory",
    "KnowledgeRelation",
    "ProjectionBackend",
    "StorageProfile",
    "compose_all",
    "decode_function",
    "decode_pair",
    "encode_function",
    "encode_pair",
    "main",
    "to_storage_profile",
]
