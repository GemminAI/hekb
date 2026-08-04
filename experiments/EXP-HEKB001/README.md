# EXP-HEKB001: Graphify & HEKB Persistence Validation

## 目的 (Purpose)

`InMemoryProjectionBackend`（テスト/デモ専用のフェイク）に代わり、実際にディスクへ
決定論的・SHA-256 コンテンツハッシュ付きで永続化する `ProjectionBackend` 実装を
検証すること。Save → Load → Hash → Replay の完全性、冪等コミット、重複検出、
オブジェクト不変性、および実マウントパス上でのストレージ検証を対象とする。

## 対象Repository (Target Repository)

`/media/psf/SSD1TB/HEKBv2`（HEKB v1.0.1、`hekb` パッケージ）

## 対象Commit (Target Commit)

`4379eb92ab5e14c6d307bc5ed4474dfef64fc2bf`
`feat(hekb): implement EXP-HEKB001 persistence validation foundation`

## 対象RFC (Target Specification)

EXP-HEKB001 v1.0.0（`specification.md` に全文保存）。この時点で `RFC-HEKB`
シリーズは存在せず、`docs/RFC_ALIGNMENT.md` がその代替として機能している。

## 実施日時 (Execution Date/Time)

2026-08-04 23:00:09 +0900

## 再現方法 (Reproduction Method)

```bash
cd /media/psf/SSD1TB/HEKBv2
source .venv/bin/activate
cd experiments
python exp_hekb_001_persistence_validation.py
```

結果は `experiments/results/exp_hekb_001.json` に上書き保存される（この
アーカイブの `results.json` はコミット時点のスナップショット）。永続化先は
`experiments/_hekb_store/`（gitignore 対象、毎回再生成される）。

## Quality Gates

```bash
cd /media/psf/SSD1TB/HEKBv2
source .venv/bin/activate
python -m pytest -q
ruff check .
ruff format --check .
python -m mypy .
```

結果: pytest 29 passed / coverage 91%（`src/hekb`）/ ruff check clean /
ruff format --check clean / mypy --strict clean。`src/hekb` は無変更。

## 結果概要 (Results Summary)

全 3 サブチェック（persistence, lineage, scale）が pass。ラウンドトリップ
同一性、決定論的リプレイ、冪等コミット、重複検出、不変性のすべてが成立。
500 件の合成データに対するルックアップレイテンシは p95 = 0.77ms
（目標 5ms 以下）。

## 主要Finding (Key Findings)

1. `hekb.category`（圏論コア）は EXP-HEKB001 の境界モデル（"HEKB は圏論に
   責任を持たない"）と矛盾する — これは HEKB 自身の設計上の自己記述であり、
   欠陥ではなく仕様側の境界モデルの誤り。
2. `hekb.storage.to_storage_profile` は宣言的サマリのみを永続化し、
   `KnowledgeRelation.mapping` および `Concept` 全体は永続化されない
   （`StorageProfile` fidelity gap）。ラウンドトリップ同一性は実際に
   永続化される範囲でのみ検証し、過大な主張はしていない。
3. "Storage ignorance" はデータベース *ドライバ* のインポート禁止であり、
   ファイル I/O 自体を禁止するものではない — これにより実ファイルベース
   バックエンドの実装が境界違反なしに可能となった。

## 未解決事項 (Open Items)

- `StorageProfile` の宣言的サマリ vs. 完全フィデリティのスコープ
  （Priority C、未決定）。
- Graphify 統合（Stage 3）は外部依存として記録のみ — 実装・スタブなし。
- 実ドキュメントコーパス（RFCv3_draft / sensos-docs / Daily Logs）は
  この時点でワークスペース内に存在せず、Stage 5/7 は合成データで代替。

## 次のEXP (Next Experiment)

EXP-HEKB002 — Closed-Loop End-to-End Verification（実 MSR/CLE パイプライン
との統合、Semantic Closure Engine の導入、MSR FieldPrior への再注入検証）。
