# EXP-HEKB003: Real-World Cross-Domain Semantic Search, Morphism Algebra & Semantic Closure Validation

- **Project**: SensOS Core & Enterprise Project / Epistemic Query & Search Engine Series
- **Date**: 2026-08-04
- **Version**: 2.0.0 (Semantic Search Engine & Geometric Ranking Expansion)
- **Status**: Proposed / Active Specification
- **Target Components**: `Graphify`, `Functorial Graph Adapter`, `HEKB Storage Engine`, `Semantic Closure Engine`, `Semantic Search Engine`, `HEKB MCP Service`, `cle-core`, `msr`
- **Upstream Sources**:
  1. Human/Ecosystem Artifacts: `RFCv3_draft`, `sensos-docs`, Git Commit History, ADRs, Architecture Reviews, Code AST (`src/`)
  2. Engine Knowledge Artifacts: `cle-core` (`HEKBCommitTransaction` / `KnowledgeDelta`)
- **Downstream Target**: Multi-Domain Semantic Context Injection Client, LLM Context Economy Injection, MSR Potential Re-injection Engine

## I. Executive Summary & Strategic Rationale

本実験 EXP-HEKB003 は、EXP-HEKB001（永続化）および EXP-HEKB002（閉環検証）の
成功を基礎とし、実際の開発・運用データ（RFC, 仕様ドキュメント, ADR, Git 履歴,
Python コード AST, レビュー文書）を Graphify および関手アダプター (F_graph) を
通じて多層インジェストし、異種ドキュメント間を跨ぐ圏論的意味検索エンジン
（Semantic Search Engine）およびクロスドメイン意味閉包（Cross-Domain Semantic
Closure S(Q)）の正当性を一括評価・検証する最終実写実験仕様である。

検索処理を単純な「キーワード照会」や「ベクトル内積（Cosine Similarity）」から
切り離し、「概念解決 → 射の代数合成 → 幾何的ランキング → 最小自己完結部分圏の
導出」という代数的・幾何学的探索プロセスとして定義・検証する。

```
 [ Human Artifacts ]                 [ Engine Knowledge ]
  (RFC, Docs, ADR, Code, Git)          (cle-core / Trajectories)
              │                                    │
              ▼                                    ▼
         [ Graphify ]                  [ HEKBCommitTransaction ]
              │                                    │
              ▼                                    │
     [ Property Graph ]                            │
              │                                    │
              ▼                                    │
  [ Functorial Graph Adapter ]                     │
   (F_graph: Graph -> C_HEKB)                      │
              │                                    │
              └─────────────────┬──────────────────┘
                                │
                                ▼
                   [ HEKB Storage Engine ]
                 (/media/psf/SSD1TB/HEKBv2)
                                │
                                ▼
                   [ Semantic Closure Engine ]
                   - Cross-Domain Morphisms (g o f)
                   - Pullback (Root Cause)
                   - Pushout (Impact Wave)
                                │
                                ▼
                   [ Semantic Search Engine ]
                   - Concept Resolution
                   - Geometric Metric Ranking
                   - False Inclusion Elimination
                                │
                                ▼
                      [ HEKB MCP Service ]
                                │
                                ▼
           [ Multi-Domain Context Economy Injection ]
         (RFC -> Code -> Commit -> ADR -> Attractor)
```

## II. Query Pipeline & Geometric Metric Ranking

### 1. End-to-End Query Pipeline

Natural Language / Concept Query → Concept Resolution → Typed Object
Lookup → Semantic Closure S(Q) → Pullback/Pushout Bound → Geometric
Ranking Engine → Context Economy Filter → MCP Context Response.

### 2. Geometric Metric Ranking Function (D_ranking)

```
D_ranking(Q, A) = w1 * D_functorial(Q, A) + w2 * L_morphism(Q, A)
                + w3 * D_potential(Q, A) + w4 * Depth_category(A)
```

- `D_functorial(Q, A)`: 関手 F_graph 上での構造的射影距離。
- `L_morphism(Q, A)`: 合成射における型付き射の最小パス長。
- `D_potential(Q, A)`: 相空間ポテンシャル場 Φ(θ) におけるマハラノビス
  アトラクター距離 D_M。
- `Depth_category(A)`: 圏階層における抽象度深度ペナルティ。

## III. Verification Objectives & Quantitative Metrics

1. Semantic Retrieval Correctness (R_semantic) — Target: 100% Deterministic
2. Morphism Composition Depth (D_comp) — Target: ≥ 4 Hops
3. False Inclusion Rate (F_inclusion) — Target: 0%
4. Cross-Domain Multi-Hop Traversal Yield (Y_cross) — Target: 100%
5. Pullback Navigation (Root Cause / Shared Prerequisite Extraction) — Target: 100% Accuracy
6. Pushout Navigation (Impact Wave Analysis) — Target: 100% Recall
7. Real-World Context Economy Ratio (C(Q)) — Target: ≤ 0.15 (`|S(Q)| / |Reachable(Q)|`)
8. Query Response Latency under Scale (τ_scale) — Target: < 10ms at p99
9. Differential Synchronization (ΔGraph → ΔC_HEKB) — Target: 0% Duplication, 100% Diff Identity

## IV. Phased Execution Matrix

| Phase | 対象データ範囲 | 主たる検証目的 | 完了基準 |
|---|---|---|---|
| Phase 1 | RFCv3_draft + sensos-docs | 人間執筆ドキュメントの Functorial Lift、クロスリファレンス完全インデックス化 | 可換図式成立、完全リプレイ再現性 |
| Phase 2 | Docs + Code (`src/`) + Git Log | 異種ドキュメント結合、Pullback/Pushout ナビゲーションの精度検証 | RFC→Code→Commit 追跡率100%、Pushout 影響範囲検出の正確性 |
| Phase 3 | Full Integration + Search Engine | 幾何的ランキング、Context Economy、差分同期の統合検証 | τ_scale<10ms、C(Q)≤0.15、F_inclusion=0%、全統合パイプラインの閉環 |

## V. Response Payload Schema for Cross-Domain Search & Closure

```json
{
  "query": {
    "raw_term": "MeaningMeasurement",
    "resolved_concept_id": "MeaningMeasurement",
    "category": "DomainConcept"
  },
  "search_metrics": {
    "retrieval_correctness": 1.0,
    "composition_depth": 4,
    "false_inclusion_rate": 0.0,
    "context_economy_ratio": 0.12,
    "execution_time_ms": 3.42
  },
  "semantic_closure": {
    "target_object": {"id": "MeaningMeasurement", "category": "DomainConcept", "sha256": "c8f912a3..."},
    "objects": [
      {"id": "RFC-MM001", "category": "SpecificationDocument", "score": 0.98},
      {"id": "MeaningMeasurement", "category": "DomainConcept", "score": 1.00},
      {"id": "meaning_mapper/abi.py", "category": "CodeImplementation", "score": 0.95},
      {"id": "commit:aef995a", "category": "GitCommit", "score": 0.89},
      {"id": "RFC-MSR01", "category": "SpecificationDocument", "score": 0.92},
      {"id": "KnowledgeDelta", "category": "CrystallizedKnowledge", "score": 0.87}
    ],
    "morphisms": [
      {"source": "RFC-MM001", "target": "MeaningMeasurement", "type": "defines"},
      {"source": "meaning_mapper/abi.py", "target": "MeaningMeasurement", "type": "implements"},
      {"source": "commit:aef995a", "target": "meaning_mapper/abi.py", "type": "modifies"},
      {"source": "RFC-MSR01", "target": "MeaningMeasurement", "type": "consumes"},
      {"source": "KnowledgeDelta", "target": "MeaningMeasurement", "type": "depends_on"}
    ],
    "proof_path": ["RFC-MM001", "MeaningMeasurement", "meaning_mapper/abi.py", "commit:aef995a"],
    "pullback_roots": ["MeaningMeasurement"],
    "pushout_wavefront": ["meaning_mapper/abi.py", "RFC-MSR01", "cle_core/crystallization.py"]
  }
}
```

## VI. Revision History

- 2026-08-04: Initial draft (v1.0.0). Established real-world multi-source ingestion targets.
- 2026-08-04: v2.0.0 — Elevated scope to Real-World Cross-Domain Semantic
  Search & Closure Engine, introduced the Semantic Search Engine layer and
  Geometric Metric Ranking Function, formalized the end-to-end Query
  Pipeline, added R_semantic, D_comp, and F_inclusion.

---

## Implementation Instructions (as supplied with this specification)

Repository status at commissioning: EXP-HEKB001 and EXP-HEKB002 complete
and pushed; `origin/main` synchronized; HEKB Storage, Semantic Closure
reference engine, CLE bridge and MCP reference already exist as the
validated baseline.

**Task**: NOT to redesign HEKB — empirically validate the existing
architecture using real project artifacts. Never rewrite production
architecture. Do not introduce speculative algorithms. Do not invent
Graphify. Do not invent Homotopy algorithms. Do not invent embeddings or
vector search. Do not modify `src/hekb` unless an actual repository
defect is discovered. Prefer `experiments/`, reference adapters, fixtures
and validation harnesses. Everything must remain deterministic and
replayable.

**Stages**: 1 — Real Repository Survey (use only repositories/documents
that actually exist; do not fabricate missing producers). 2 — Graphify
Validation (structural extractor only; reference adapters if interfaces
are missing). 3 — Functorial Lift Validation (typed morphisms: defines,
consumes, implements, modifies, references, documents; no category-theory
redesign). 4 — Cross-Domain Semantic Search (reference layer in
`experiments/`; purely categorical, not vector search). 5 — Real Artifact
Validation (multi-hop traversal, deterministic replay, proof paths,
pullback roots, pushout wavefront). 6 — Performance (cross-domain yield,
closure correctness, pullback accuracy, pushout recall, context economy,
search latency, differential synchronization).

Quality gates before commit: pytest, coverage, ruff check, ruff format
--check, mypy --strict. Do not commit automatically — wait for approval.
