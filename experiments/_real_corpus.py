"""EXP-HEKB003 Stage 1/2/3: assembles the real, multi-repository corpus.

Real repository survey (Stage 1's deliverable) is `survey()`'s return
value: exactly which files this experiment reads, and nothing invented.
Every node/edge in the resulting `PropertyGraph` traces back to a real
file, a real class definition, a real backtick reference, or a real git
commit — see `_real_artifact_extractors.py` for how each is read.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from _graphify_reference import PropertyGraph, PropertyGraphEdge, PropertyGraphNode
from _real_artifact_extractors import (
    Corpus,
    build_nodes_and_edges_for_commits,
    build_nodes_and_edges_for_markdown_file,
    build_nodes_and_edges_for_python_file,
    extract_python_classes,
    node_id_for_path,
)

HOME = Path.home()
HEKB_ROOT = Path(__file__).resolve().parent.parent

MSR_ROOT = HOME / "meaning-space-runtime"
CLE_ROOT = HOME / "categorical-lift-engine"

MSR_PYTHON_FILES = (
    "src/msr/abi.py",
    "src/msr/field.py",
    "src/msr/dynamics.py",
    "src/msr/runtime.py",
    "src/msr/host.py",
    "src/msr/stability.py",
    "src/msr/errors.py",
    "src/msr/reference.py",
    "src/msr/adapters/hekb.py",
)
MSR_MARKDOWN_FILES = (
    "RFC-MSR01.md",
    "docs/RFC_ALIGNMENT.md",
    "docs/ARCHITECTURE.md",
    "docs/BOUNDARIES.md",
)
MSR_COMMIT_TARGETS = ("src/msr/abi.py", "src/msr/runtime.py")

CLE_PYTHON_FILES = (
    "src/cle/abi/outputs.py",
    "src/cle/abi/inputs.py",
    "src/cle/categorical_lift/engine.py",
    "src/cle/errors.py",
)
CLE_MARKDOWN_FILES = (
    "docs/RFC_ALIGNMENT.md",
    "docs/ARCHITECTURE.md",
    "docs/BOUNDARIES.md",
)
CLE_COMMIT_TARGETS = ("src/cle/categorical_lift/engine.py",)

HEKB_PYTHON_FILES = (
    "src/hekb/category.py",
    "src/hekb/models.py",
    "src/hekb/runtime.py",
    "src/hekb/storage.py",
)
HEKB_MARKDOWN_FILES = (
    "docs/architecture.md",
    "docs/api.md",
    "docs/RFC_ALIGNMENT.md",
)
HEKB_COMMIT_TARGETS = ("src/hekb/category.py",)

GIT_COMMIT_LIMIT = 2


def _corpus_for(
    name: str, root: Path, markdown: tuple[str, ...], python: tuple[str, ...]
) -> Corpus:
    return Corpus(
        name=name,
        root=root,
        markdown_files=tuple(root / p for p in markdown),
        python_files=tuple(root / p for p in python),
    )


CORPORA = (
    _corpus_for("msr", MSR_ROOT, MSR_MARKDOWN_FILES, MSR_PYTHON_FILES),
    _corpus_for("cle", CLE_ROOT, CLE_MARKDOWN_FILES, CLE_PYTHON_FILES),
    _corpus_for("hekb", HEKB_ROOT, HEKB_MARKDOWN_FILES, HEKB_PYTHON_FILES),
)
COMMIT_TARGETS: dict[str, tuple[str, ...]] = {
    "msr": MSR_COMMIT_TARGETS,
    "cle": CLE_COMMIT_TARGETS,
    "hekb": HEKB_COMMIT_TARGETS,
}


@dataclass(frozen=True, slots=True)
class Survey:
    """Stage 1's real repository survey: exactly what was read."""

    repositories: tuple[str, ...]
    markdown_files: tuple[str, ...]
    python_files: tuple[str, ...]
    commit_targets: tuple[str, ...]
    vocabulary_size: int

    def as_dict(self) -> dict[str, Any]:
        return {
            "repositories": list(self.repositories),
            "markdown_files": list(self.markdown_files),
            "python_files": list(self.python_files),
            "commit_targets": list(self.commit_targets),
            "vocabulary_size": self.vocabulary_size,
        }


def build_vocabulary() -> frozenset[str]:
    """Every real top-level class name across every curated Python file --
    not a hand-picked list."""
    names: set[str] = set()
    for corpus in CORPORA:
        for path in corpus.python_files:
            names.update(extract_python_classes(path))
    return frozenset(names)


def build_real_property_graph() -> tuple[PropertyGraph, Survey]:
    vocabulary = build_vocabulary()
    concept_nodes = tuple(
        PropertyGraphNode(id=name, category="DomainConcept") for name in sorted(vocabulary)
    )

    nodes: dict[str, PropertyGraphNode] = {n.id: n for n in concept_nodes}
    edges: list[PropertyGraphEdge] = []
    markdown_read: list[str] = []
    python_read: list[str] = []
    commit_targets_read: list[str] = []

    for corpus in CORPORA:
        for path in corpus.python_files:
            node, file_edges = build_nodes_and_edges_for_python_file(path, corpus, vocabulary)
            nodes[node.id] = node
            edges.extend(file_edges)
            python_read.append(node_id_for_path(path, corpus))

        for path in corpus.markdown_files:
            node, file_edges = build_nodes_and_edges_for_markdown_file(path, corpus, vocabulary)
            nodes[node.id] = node
            edges.extend(file_edges)
            markdown_read.append(node_id_for_path(path, corpus))
            for edge in file_edges:
                if edge.kind == "references" and edge.target not in nodes:
                    category = (
                        "SpecificationDocument"
                        if edge.target.endswith(".md")
                        else "CodeImplementation"
                    )
                    nodes[edge.target] = PropertyGraphNode(id=edge.target, category=category)

        for relative in COMMIT_TARGETS[corpus.name]:
            path = corpus.root / relative
            commit_nodes, commit_edges = build_nodes_and_edges_for_commits(
                path, corpus, GIT_COMMIT_LIMIT
            )
            for commit_node in commit_nodes:
                nodes[commit_node.id] = commit_node
            edges.extend(commit_edges)
            commit_targets_read.append(node_id_for_path(path, corpus))

    graph = PropertyGraph(nodes=tuple(nodes.values()), edges=tuple(edges))
    survey = Survey(
        repositories=tuple(corpus.name for corpus in CORPORA),
        markdown_files=tuple(markdown_read),
        python_files=tuple(python_read),
        commit_targets=tuple(commit_targets_read),
        vocabulary_size=len(vocabulary),
    )
    return graph, survey


__all__ = ["Survey", "build_real_property_graph", "build_vocabulary"]
