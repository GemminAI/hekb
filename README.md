# HEKB

[![CI](https://img.shields.io/github/actions/workflow/status/GemminAI/hekb/ci.yml?branch=main&label=CI)](https://github.com/GemminAI/hekb/actions)
[![Release](https://img.shields.io/github/v/release/GemminAI/hekb)](https://github.com/GemminAI/hekb/releases)
[![License](https://img.shields.io/github/license/GemminAI/hekb)](LICENSE)

**A knowledge operating substrate.** HEKB stores facts, relates them, and finds them again.

---

## Why HEKB?

HEKB provides **content-addressed knowledge storage** where identity is derived from the fact itself rather than assigned by the application.

Reasoning systems need a place for facts that independent writers can name the same way, whose names prove their contents, and that the store itself never interprets.

Databases store rows. Vector indexes find similar vectors. Graph engines traverse edges. None of them make identity a mathematical property of the fact.

**HEKB exists to be that layer—and to stop there.**

---

## Quick Example

```python
from hekb import HextObject, HextKind, KnowledgeStore

store = KnowledgeStore()

object_id = store.put(
    HextObject(
        kind=HextKind.DOCUMENT,
        labels={
            "text": "a kettle boils water"
        },
    )
)

print(store.get(object_id).labels["text"])
# a kettle boils water
```

---

## Core Concepts

### HEXT Object

An immutable fact.

Its identifier is the **BLAKE2b-256 hash of its canonical representation**.

The same fact always has the same identifier everywhere.

### Morphism

A typed, weighted relationship between two HEXT objects.

### Retrieval

HEKB exposes three retrieval primitives:

- nearest
- neighbours
- geodesic

HEKB does **not**:

- embed text
- resolve entities
- rank importance
- infer meaning
- evaluate risk

It stores attributes without interpreting them.

---

## Comparison

| | Vector DB | Graph DB | Knowledge Graph | NVS-Kernel | **HEKB** |
|---|---|---|---|---|---|
| **Primary job** | Approximate similarity | Property graph | Ontology & inference | Runtime safety & control | Content-addressed facts |
| **Identity** | User-defined | User-defined | Entity resolution | Runtime/session state | **Hash of canonical content** |
| **Makes decisions** | Ranking | Planner | Inference | Yes | **No** |
| **Best for** | Semantic search | Complex traversal | Knowledge reasoning | Runtime control | Stable, immutable facts |

---

## HEKB vs NVS-Kernel

> **HEKB stores. NVS-Kernel decides.**

NVS-Kernel is a client of HEKB.

HEKB has no dependency on NVS-Kernel.

See **docs/NVS-Kernel.md** for architectural boundaries.

---

## Install

```bash
pip install hekb
```

Or clone the repository and run:

```
examples/quickstart.py
```

For the server, CLI, C++ runtime, and MCP interface, see:

- docs/Quickstart.md

---

## Documentation

- Quickstart
- Examples
- ABI
- API Reference
- Python API
- FAQ
- Documentation Site
- SECURITY
- CONTRIBUTING

---

## License

Apache License 2.0

See **LICENSE** and **NOTICE** for details.
