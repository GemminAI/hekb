"""A runnable walkthrough of HEKB's core operations.

Run with:

    uv run python examples/basic_usage.py
"""

from __future__ import annotations

from hekb import (
    CategoryAxiomViolation,
    Concept,
    HEKBCoreRuntime,
    HomotopyViolation,
    InMemoryProjectionBackend,
    KnowledgeRelation,
)


def main() -> None:
    runtime = HEKBCoreRuntime(InMemoryProjectionBackend())

    # 1. Ingest objects (Concepts) into the knowledge category.
    runtime.ingest_object(Concept(id="A", elements=frozenset({"a1", "a2"})))
    runtime.ingest_object(Concept(id="B", elements=frozenset({"b1", "b2"})))
    runtime.ingest_object(Concept(id="C", elements=frozenset({"c1"})))
    print("Objects ingested: A, B, C")

    # 2. Ingest a well-formed morphism -- validated, then persisted.
    f = KnowledgeRelation(id="f", source="A", target="B", mapping={"a1": "b1", "a2": "b2"})
    runtime.ingest_morphism(f)
    print(f"Morphism {f.id!r} accepted and persisted.")

    # 3. A malformed morphism (not total over its source) is rejected --
    #    and nothing about it reaches storage.
    try:
        runtime.ingest_morphism(
            KnowledgeRelation(id="bad", source="A", target="B", mapping={"a1": "b1"})
        )
    except CategoryAxiomViolation as exc:
        print(f"Rejected as expected: {exc}")

    # 4. Pushout: given a span C --p--> A and C --q--> B sharing apex C,
    #    compute the pushout object and its injections.
    p = KnowledgeRelation(id="p", source="C", target="A", mapping={"c1": "a1"})
    q = KnowledgeRelation(id="q", source="C", target="B", mapping={"c1": "b1"})
    runtime.ingest_morphism(p)
    runtime.ingest_morphism(q)

    pushout_object, _iota_a, _iota_b = runtime.category.pushout(p, q)
    print(
        f"Pushout of A and B over C has {len(pushout_object.elements)} elements "
        f"(a1 and b1 were identified via C)."
    )

    # 5. The Homotopic Update Law: an update U is only admitted if its
    #    naturality square commutes.
    runtime.ingest_object(Concept(id="UA", elements=frozenset({"ua1", "ua2"})))
    runtime.ingest_object(Concept(id="UB", elements=frozenset({"ub1", "ub2"})))
    sigma_a = KnowledgeRelation(
        id="sigma_a", source="A", target="UA", mapping={"a1": "ua1", "a2": "ua2"}
    )
    sigma_b = KnowledgeRelation(
        id="sigma_b", source="B", target="UB", mapping={"b1": "ub1", "b2": "ub2"}
    )
    runtime.ingest_morphism(sigma_a)
    runtime.ingest_morphism(sigma_b)

    # A valid update: consistent with sigma_a/sigma_b/f.
    valid_u_f = KnowledgeRelation(
        id="u_f", source="UA", target="UB", mapping={"ua1": "ub1", "ua2": "ub2"}
    )
    runtime.ingest_update(sigma_a, f, sigma_b, valid_u_f)
    print(f"Update {valid_u_f.id!r} accepted: naturality square commutes.")

    # A broken update: disagrees with the required naturality square.
    broken_u_f = KnowledgeRelation(
        id="u_f_broken", source="UA", target="UB", mapping={"ua1": "ub2", "ua2": "ub1"}
    )
    try:
        runtime.ingest_update(sigma_a, f, sigma_b, broken_u_f)
    except HomotopyViolation as exc:
        print(f"Rejected as expected: {exc}")

    # 6. Export a frozen snapshot for downstream consumers.
    snapshot = runtime.export_epistemic_graph()
    print(f"Exported snapshot: {len(snapshot.vertices)} vertices, {len(snapshot.edges)} edges.")


if __name__ == "__main__":
    main()
