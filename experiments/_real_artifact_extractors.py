"""EXP-HEKB003's real-artifact structural extractors.

Reference adapters standing in for Graphify — not Graphify itself. No
Graphify repository exists anywhere in this workspace (recorded in
EXP-HEKB001's `docs/RFC_ALIGNMENT.md`, unchanged since); Stage 2's own
instruction is explicit: *"If interfaces are missing, implement reference
adapters only."* Every function here reads a **real** file from a real
sibling repository and emits real `PropertyGraph` nodes/edges — no fixture
data, no fabricated content, no regex guessing at code structure where a
real parser exists.

Three modalities:

- **Markdown**: backtick-quoted vocabulary terms become `"documents"`
  edges; backtick-quoted paths that resolve to a real file in the corpus
  become `"references"` edges — discovered by scanning real text, not
  hand-picked, so real doc-to-doc chains emerge on their own.
- **Python**: top-level class definitions matching the vocabulary become
  `"implements"` edges, found via `ast.parse` — a real parser, not a
  regex.
- **Git**: real commit hashes touching a file, via a real `git log`
  subprocess call against the real repository, become `"modified_by"`
  edges.
"""

from __future__ import annotations

import ast
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path

from _graphify_reference import PropertyGraphEdge, PropertyGraphNode

_BACKTICK_TOKEN = re.compile(r"`([^`\s]+)`")


@dataclass(frozen=True, slots=True)
class Corpus:
    """The real files this experiment draws from, grouped by repository."""

    name: str
    root: Path
    markdown_files: tuple[Path, ...]
    python_files: tuple[Path, ...]


def node_id_for_path(path: Path, corpus: Corpus) -> str:
    return f"{corpus.name}/{path.relative_to(corpus.root)}"


def extract_python_classes(path: Path) -> tuple[str, ...]:
    """Real top-level class names defined in `path`, via `ast.parse`."""
    tree = ast.parse(path.read_text(), filename=str(path))
    return tuple(node.name for node in ast.iter_child_nodes(tree) if isinstance(node, ast.ClassDef))


def extract_git_commits(path: Path, repo_root: Path, limit: int) -> tuple[str, ...]:
    """Real commit hashes touching `path`, most recent first."""
    result = subprocess.run(
        [
            "git",
            "log",
            f"--max-count={limit}",
            "--format=%H",
            "--",
            str(path.relative_to(repo_root)),
        ],
        cwd=repo_root,
        capture_output=True,
        text=True,
        check=True,
    )
    return tuple(line.strip() for line in result.stdout.splitlines() if line.strip())


def extract_backtick_tokens(path: Path) -> tuple[str, ...]:
    """Every backtick-quoted token in a real Markdown file's real text."""
    return tuple(_BACKTICK_TOKEN.findall(path.read_text()))


def resolve_path_reference(token: str, corpus: Corpus) -> Path | None:
    """If `token` names a real file that exists in `corpus.root` (after
    stripping a `RFCv3_draft/rfc/MSR/`-style external-workspace prefix
    this repository's docs sometimes use for a sibling that isn't actually
    checked out here), return its real path; otherwise `None`.
    """
    candidate = corpus.root / token
    if candidate.is_file():
        return candidate
    return None


def build_nodes_and_edges_for_python_file(
    path: Path,
    corpus: Corpus,
    vocabulary: frozenset[str],
) -> tuple[PropertyGraphNode, tuple[PropertyGraphEdge, ...]]:
    file_id = node_id_for_path(path, corpus)
    node = PropertyGraphNode(id=file_id, category="CodeImplementation")
    classes = extract_python_classes(path)
    edges = tuple(
        PropertyGraphEdge(
            id=f"{file_id}_implements_{class_name}",
            source=file_id,
            target=class_name,
            kind="implements",
        )
        for class_name in classes
        if class_name in vocabulary
    )
    return node, edges


def build_nodes_and_edges_for_markdown_file(
    path: Path,
    corpus: Corpus,
    vocabulary: frozenset[str],
) -> tuple[PropertyGraphNode, tuple[PropertyGraphEdge, ...]]:
    file_id = node_id_for_path(path, corpus)
    node = PropertyGraphNode(id=file_id, category="SpecificationDocument")
    tokens = extract_backtick_tokens(path)

    concept_edges = tuple(
        PropertyGraphEdge(
            id=f"{file_id}_documents_{token}",
            source=file_id,
            target=token,
            kind="documents",
        )
        for token in dict.fromkeys(tokens)  # de-duplicate, keep first-seen order
        if token in vocabulary
    )

    reference_edges: list[PropertyGraphEdge] = []
    for token in dict.fromkeys(tokens):
        resolved = resolve_path_reference(token, corpus)
        if resolved is not None and resolved != path:
            target_id = node_id_for_path(resolved, corpus)
            reference_edges.append(
                PropertyGraphEdge(
                    id=f"{file_id}_references_{target_id}",
                    source=file_id,
                    target=target_id,
                    kind="references",
                )
            )

    return node, concept_edges + tuple(reference_edges)


def build_nodes_and_edges_for_commits(
    path: Path,
    corpus: Corpus,
    limit: int,
) -> tuple[tuple[PropertyGraphNode, ...], tuple[PropertyGraphEdge, ...]]:
    file_id = node_id_for_path(path, corpus)
    commit_hashes = extract_git_commits(path, corpus.root, limit)
    nodes = tuple(
        PropertyGraphNode(id=f"commit:{sha[:7]}", category="GitCommit") for sha in commit_hashes
    )
    edges = tuple(
        PropertyGraphEdge(
            id=f"{file_id}_modified_by_{sha[:7]}",
            source=file_id,
            target=f"commit:{sha[:7]}",
            kind="modified_by",
        )
        for sha in commit_hashes
    )
    return nodes, edges


__all__ = [
    "Corpus",
    "build_nodes_and_edges_for_commits",
    "build_nodes_and_edges_for_markdown_file",
    "build_nodes_and_edges_for_python_file",
    "extract_backtick_tokens",
    "extract_git_commits",
    "extract_python_classes",
    "node_id_for_path",
    "resolve_path_reference",
]
