# EXP-HEKB001: Graphify & HEKB Persistence Validation

Empirical Validation of Structural Ingestion, Epistemic Mapping & Storage Identity

- **Project**: SensOS Core & Enterprise Project / Knowledge Persistence Series
- **Date**: 2026-08-04
- **Version**: 1.0.0
- **Status**: Proposed / Active Specification
- **Target Components**: Graphify (Structural Engine), HEKBv2 (`/media/psf/SSD1TB/HEKBv2`), cle-core (CommitCandidate Handoff)
- **Upstream Sources**:
  1. RFCv3_draft / sensos-docs (Human-written Markdown Documentation)
  2. `HEKBCommitTransaction` / `CommitCandidate` (CLE EXP-Ubuntu005 Outputs)
- **Downstream Target**: HEKB Epistemic Graph Storage & State Persistence Layer

## I. Executive Summary & Architectural Rationale

SensOS において幾何測定（MM）→ 相空間軌跡（MSR）→ 圏論的昇華（CLE）を経て抽出された不可変知識（KnowledgeDelta）および、人間が記述した仕様文書（RFC / Docs）を統合し、単一の意味論的幾何グラフとして永続化・決定論的再現性を検証する実験 EXP-HEKB001 を定義する。

本実験の要旨は、ストレージパス `/media/psf/SSD1TB/HEKBv2` を単なるファイル置き場ではなく、以下の多層パイプラインの最終集約点として実証することにある。

```
 [ Markdown / RFC / Docs ]
            │
            ▼
       [ Graphify ]               ── "Structuralization" (Nodes, Edges, Dependencies)
            │
            ▼
     [ Property Graph ]
            │
            ▼
       [ HEKB Object ]            ── "Semanticization" (Concepts, Morphisms, Topologies)
            │
            ▼
  [ HEKB Persistence (v2) ]       ── Identity, Hash, Determinism & ACIDO Checks
  (/media/psf/SSD1TB/HEKBv2)
```

## II. Dual Ingestion Pipelines Under Test

本実験では、HEKBv2 に対する 2 系統の知識インジェストパスを同時検証する。

### 1. Structural Ingestion Path (Human Knowledge)

- Input: RFCv3_draft (Phase 1) → sensos-docs (Phase 2)
- Process: Graphify による AST/リンク解析 → Property Graph 構成 → HEKB Concept/Morphism 変換
- Role: 人間が記述した形式仕様の構造および依存関係（defines, consumes, extends）の抽出。

### 2. Epistemic Lift Path (Engine Knowledge)

- Input: cle-core 由来の `HEKBCommitTransaction` (`CommitCandidate`)
- Process: CLE 結晶化相転移（ΔS < -δ）のコミットトランザクション受入
- Role: AI/幾何エンジンが軌跡から自動抽出した位相不変量および不変構造の組み込み。

## III. Verification Objectives & Target Metrics

EXP-HEKB001 では以下の 5 項目を定量的合否基準として検証する。

1. **Graphification & Schema Conversion Fidelity (Φ_graph)** — Target: 100%
2. **Round-Trip Identity & Deterministic Replay (I_replay)** — Target: 100%. `Hash(Load(Save(O))) ≡ Hash(O)`
3. **Transaction Isolation & Idempotency Check** — Target: 100% Zero-Duplication
4. **Cross-Reference Lineage Validation** — RFC-MM001 (defines MeaningMeasurement) と RFC-MSR01 (consumes MeaningMeasurement) 型の依存関係が不変な射としてインデックス化されること。
5. **Multi-Layer Search & Topological Retrieval Benchmark** — Target: < 5ms lookup time

## IV. Phased Execution Matrix

| Phase | 対象データソース | 主たる検証目的 | 完了条件 |
|---|---|---|---|
| Phase 1 | RFCv3_draft | 仕様書群の決定論的パース、defines/consumes エッジ抽出、HEKB スキーマ適合性テスト | 100% リプレイ再現性と構造ツリーの完全保存 |
| Phase 2 | sensos-docs | 複雑なクロスリファレンス、リファクタリング履歴（Lineage）のグラフ統合テスト | ドキュメント群全体の無矛盾インデックス化 |
| Phase 3 | Full Vault & Daily Logs | 非定型ドキュメントおよび大容量データの永続化スループット・スケールテスト | `/media/psf/SSD1TB/HEKBv2` 上での高速応答維持 |

## V. Revision History

- 2026-08-04: Initial draft of EXP-HEKB001 specification (v1.0.0). Standardized dual ingestion pipeline, round-trip identity verification metrics, and phased validation target matrix.

---

## Implementation Instructions (as supplied with this specification)

Repository: `~/HEKBv2` (resolved to the actual working copy at `/media/psf/SSD1TB/HEKBv2`)

**Development Policy**: Implementation First. The implementation is the source of truth. The EXP specification is an experimental hypothesis, not an implementation contract.

**Stages**:

1. Repository Audit — audit current persistence model, object model, graph representation, hashing, storage identity, replay capability, transaction model. Produce an implementation matrix. Do not modify code yet.
2. Boundary Audit — verify HEKB remains responsible only for persistence, identity, graph storage, replay, indexing; must NOT become responsible for Meaning Measurement, Trajectory generation, Category theory, Graphify parsing. Record any leaked responsibility.
3. Graphify Integration — treat Graphify as an external producer; validate the pipeline Markdown → Graphify → Property Graph → HEKB Object → Persistence; do not reimplement Graphify, only validate the interface.
4. Persistence Validation — validate Save → Load → Hash → Replay; measure identity preservation, SHA-256 stability, deterministic replay, object immutability, idempotent commit, duplicate detection.
5. Cross Reference Validation — use RFCv3_draft first, then sensos-docs; validate defines/consumes/extends/references become deterministic graph morphisms.
6. Storage Validation — target storage `/media/psf/SSD1TB/HEKBv2`; validate persistence, lookup, replay, transaction isolation, recovery. Correctness before performance.
7. Large Scale Validation — only if Stage 6 passes; measure scalability, storage growth, lookup latency, replay determinism.
8. Gap Analysis — classify findings as Priority A (implementation defect), B (RFC obsolete), C (architectural decision), D (future experiment). Do not modify implementation merely to satisfy wording.
9. Implementation — fix only verified implementation defects; quality gates must remain green after every change.
10. RFC Realignment — only after implementation is complete; update `docs/RFC_ALIGNMENT.md` and `CHANGELOG.md`; record validated behavior, rejected assumptions, implementation-first decisions. Do not rewrite RFCs yet.

**Deliverables**: implementation matrix, architecture review, persistence validation, replay metrics, graph statistics, quality gates, commit summary.

Stop only if a genuine architectural decision is required. Otherwise continue autonomously until HEKB reaches a validated experimental state.
