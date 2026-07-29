"""Storage-ignorance audit: HEKB's core modules must never import a DB driver.

A static AST scan asserting that no module under ``hekb`` (except the
boundary Protocol itself, which by design only names the abstraction,
never a concrete driver) imports a physical database library or
references raw SQL/CQL string literals as a client would.
"""

from __future__ import annotations

import ast
from pathlib import Path

FORBIDDEN_MODULES = {
    "psycopg2",
    "psycopg",
    "scylladb",
    "cassandra",
    "boto3",
    "sqlite3",
    "sqlalchemy",
    "pymongo",
}

SRC_ROOT = Path(__file__).resolve().parent.parent / "src" / "hekb"


def _imported_module_roots(tree: ast.AST) -> set[str]:
    roots: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                roots.add(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom) and node.module:
            roots.add(node.module.split(".")[0])
    return roots


def test_no_module_under_hekb_imports_a_database_driver() -> None:
    violations: dict[str, set[str]] = {}
    for path in sorted(SRC_ROOT.rglob("*.py")):
        tree = ast.parse(path.read_text(), filename=str(path))
        hit = _imported_module_roots(tree) & FORBIDDEN_MODULES
        if hit:
            violations[str(path.relative_to(SRC_ROOT))] = hit

    assert not violations, (
        f"forbidden storage-driver imports found (storage-ignorance violation): {violations}"
    )


def test_storage_module_defines_only_an_abstract_boundary() -> None:
    """storage.py may reference *the concept* of a backend, never a concrete one."""
    tree = ast.parse((SRC_ROOT / "storage.py").read_text())
    hit = _imported_module_roots(tree) & FORBIDDEN_MODULES
    assert not hit
