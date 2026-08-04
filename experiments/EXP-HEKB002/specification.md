# EXP-HEKB002: Epistemic Storage, Semantic Closure Query & Knowledge Reuse Validation

Closed-Loop End-to-End Verification

- **Project**: SensOS Core & Enterprise Project / Knowledge Persistence Series
- **Date**: 2026-08-04
- **Version**: 2.0.0 (Post-Semantic-Closure Expansion)
- **Status**: Proposed / Active Specification
- **Target Components**: `semantic-annotator-core`, `meaning-mapper`, `msr`, `nvs-kernel`, `cle-core`, `HEKBv2` (`/media/psf/SSD1TB/HEKBv2`), `Graphify`, `Functorial Graph Adapter`, `Semantic Closure Engine`, `HEKB MCP Service`
- **Upstream Sources**:
  1. `cle-core` (`HEKBCommitTransaction` / `CommitCandidate`)
  2. `Graphify` (Human Knowledge Property Graph from `RFCv3_draft` & `sensos-docs`)
- **Downstream Target**: HEKB Storage Engine, MCP Query Client (LLM Context Economy Injection / MSR Re-injection)

## I. Executive Summary & Closed-Loop Architecture

本実験 EXP-HEKB002 は、SensOS において「ローカルモデル/観測エンジンが意味を生成し、
幾何・位相変換を経て不変知識として HEKB へ蓄積され、Semantic Closure Engine および
MCP (Model Context Protocol) を通じて意味保存的に再参照・再利用される」という
一気通貫のエンドツーエンド閉環パイプラインの完全動作を実証することを目的とする。

EXP-HEKB001 がストレージ単体の決定論的ファイル保存と形式変換の検証にとどまるのに
対し、EXP-HEKB002 では `/media/psf/SSD1TB/HEKBv2` への物理永続化、圏論的射の合成
（Morphism Composition g∘f）に基づく意味閉包クエリ（Semantic Closure Query）、
および MSR ポテンシャル場へのアトラクター再注入までの全経路を同一ループ内で
統合・計測する。

```
 [ Local Model / Raw Sensor ]
              │
              ▼
  [ semantic-annotator-core ]
              │
              ▼
    [ Meaning Mapper (MM) ]       ── MeaningMeasurement (theta, Sigma)
              │
              ▼
     [ MSR / NVS-Kernel ]         ── StabilizedTrajectory
              │
              ▼
      [ cle-core (CLE) ]          ── Functorial Lift & Crystallization
              │
              ▼
   [ HEKBCommitTransaction ]      ── Pure Knowledge Object (KnowledgeDelta)
              │
              ├─────────────────────────────────┐ (Dual-Inflow Integration)
              ▼                                 ▼
   [ HEKB Storage Engine ] ◄────────── [ Graphify Pipeline ]
  (/media/psf/SSD1TB/HEKBv2)           (Markdown / RFC / Docs)
              │                                 │
              │                                 ▼
              │                    [ Functorial Graph Adapter ]
              │                    (F_graph: Graph -> C_HEKB)
              │                                 │
              └────────────────┬────────────────┘
                               │
                               ▼
                [ Semantic Closure Engine ]    ── Morphism Algebra & Composition (g o f)
                               │                  Pullback (Premise) / Pushout (Impact)
                               ▼
                      [ HEKB MCP Service ]     ── Model Context Protocol (Query API)
                               │
                               ▼
                   [ Knowledge Reuse / MSR ]   ── Re-injection & Context Economy Injection
```

## II. Verification Pipeline & Dual Ingestion Pathways

1. **Engine Knowledge Flow (CLE → HEKB Storage)** — `cle-core` が
   `StabilizedTrajectory` から抽出した `HEKBCommitTransaction`
   (`CommitCandidate`) を ACIDO トランザクション処理により物理書き込み。
2. **Human Knowledge Flow (Graphify → Functorial Graph Adapter → HEKB Storage)**
   — `RFCv3_draft`/`sensos-docs` の Property Graph を関手的に HEKB 概念
   ノード・型付き射（Definition, Dependency, Refinement, Context）へ変換・永続化。
3. **Closed-Loop Retrieval & Reuse Flow (Semantic Closure MCP → Client Engine)**
   — クエリ概念 Q に対し、代数的探索ステップ（Target Object → Typed Morphisms
   → Composition g∘f → Semantic Closure S(Q)）を経て最小自己完結型部分圏を
   決定論的に構築・返却。

## III. Target Metrics & Acceptance Criteria

1. End-to-End Pipeline Execution Yield (Y_e2e) — Target: 100% (0 Uncaught Exceptions)
2. Persistence Hash Identity & Replay Determinism (I_replay) — Target: 100% Bit-Identical
3. Dual-Source Cross-Reference Alignment (A_cross) — Target: 100%
4. MCP Query Lookup Latency (τ_mcp) — Target: < 5ms at p99
5. Idempotent Double-Commit Preservation — Target: 0% Duplication
6. Closed-Loop Knowledge Re-injection Validation — MSR `FieldPrior` への
   アトラクターウェルパラメータ再注入と Basin Recovery への寄与を証明。
7. Semantic Closure Query Correctness (S_closure) — Target: 100% Deterministic
   Closure（Determinism, Type Consistency, Functoriality Preservation,
   Pullback Navigation, Pushout Navigation, Minimal Self-Containment）。

## IV. Phased Execution Plan

| Phase | 対象データ / モジュール | 主たる検証目的 | 完了基準 |
|---|---|---|---|
| Phase 1 | Single Trajectory + RFCv3_draft | 最小単位の CLE コミット→HEKB 保存→Closure 抽出→MCP 検索の疎通確認 | Save→Closure Query の不変量ハッシュ一致 |
| Phase 2 | Batch Trajectories + sensos-docs | 型付き射インデックス化、Pullback/Pushout ナビゲーション、冪等性検証 | 重複ゼロ、共通前提と影響範囲の正確な導出 |
| Phase 3 | Full E2E Closed-Loop | 観測→CLE→HEKB→Closure Engine→MCP→MSR へのアトラクター再ロード | MSR ポテンシャル場の正常更新 |

## V. Response Payload Schema Specification

```json
{
  "query_concept_id": "8f3b21a0-6c4d-4e9f-9a12-0123456789ab",
  "target_object": {
    "id": "KnowledgeDelta",
    "type": "CrystallizedKnowledge",
    "homotopy_hash": "aef995a28c...",
    "betti_numbers": [1, 0, 0]
  },
  "semantic_closure": {
    "objects": [
      {"id": "KnowledgeDelta", "category": "Concept"},
      {"id": "StabilizedTrajectory", "category": "PhaseSpaceTrajectory"},
      {"id": "RFC-CLE001", "category": "SpecificationDocument"},
      {"id": "cle_core/crystallization.py", "category": "CodeImplementation"},
      {"id": "MeaningMeasurement", "category": "MeasurementObject"},
      {"id": "RFC-MM001", "category": "SpecificationDocument"}
    ],
    "morphisms": [
      {"source": "KnowledgeDelta", "target": "StabilizedTrajectory", "type": "crystallized_from"},
      {"source": "StabilizedTrajectory", "target": "RFC-CLE001", "type": "produced_by"},
      {"source": "RFC-CLE001", "target": "cle_core/crystallization.py", "type": "implemented_by"},
      {"source": "KnowledgeDelta", "target": "MeaningMeasurement", "type": "depends_on"},
      {"source": "MeaningMeasurement", "target": "RFC-MM001", "type": "defined_in"}
    ],
    "derived_compositions": [
      {"morphism": "m_derived: RFC-MM001 -> KnowledgeDelta", "formula": "m_crys o m_dep o m_def"}
    ],
    "pullback_roots": ["MeaningMeasurement"],
    "pushout_wavefront": ["abi.py", "RFC-CLE001"]
  },
  "is_minimal_self_contained": true,
  "execution_time_ms": 1.85
}
```

## VI. Revision History

- 2026-08-04: Initial draft (v1.0.0).
- 2026-08-04: v2.0.0 — Elevated MCP Query to Semantic Closure Query, added
  Semantic Closure Engine and Functorial Graph Adapter, defined
  Pullback/Pushout navigation criteria, standardized the JSON schema.

---

## Implementation Instructions (as supplied with this specification)

Repository: `~/HEKBv2` (`/media/psf/SSD1TB/HEKBv2`)

**Development Policy**: Build only on documented extension points. Do not
introduce speculative architecture. Reuse Graphify, Functorial Graph
Adapter, Semantic Closure Engine, and MCP integration exactly as specified
in EXP-HEKB002 v2.0.0. Preserve deterministic replay, immutable objects,
content-addressed identity, and 100% reproducibility. Validate the
complete closed-loop: Local Model → MM → MSR → NVS-Kernel → CLE → HEKB
Storage → Semantic Closure Query → MCP → MSR re-injection.

Phase 1 explicitly authorized building deterministic reference components
(reference Graphify producer, Functorial Graph Adapter, Semantic Closure
reference engine, MCP reference query interface) as experiment harnesses
only — not production Graphify.

Quality gates (pytest, coverage, ruff check, ruff format --check,
mypy --strict) must pass before commit; commit only after approval.
