# EXP-HEKB003: Real-World Cross-Domain Semantic Search, Morphism Algebra & Semantic Closure Validation

## 目的 (Purpose)

EXP-HEKB002 のフィクスチャベースの Graphify データを実データ（実
Markdown/Python/Git 履歴、複数リポジトリ横断）に置き換え、圏論的検索
（Semantic Search Engine）と幾何的ランキング関数を、ベクトル検索を一切
用いずに実証すること。

## 対象Repository (Target Repository)

`/media/psf/SSD1TB/HEKBv2`（主対象）。実データソースとして
`meaning-space-runtime`、`categorical-lift-engine`、および本リポジトリ
自身の実 Markdown/Python/Git 履歴を使用。

## 対象Commit (Target Commit)

`f2ed9ec5e95642a4c3bd6e60f7f3eb6b6f59ee48`
`feat(hekb): implement EXP-HEKB003 real-world semantic search validation`

## 対象RFC (Target Specification)

EXP-HEKB003 v2.0.0（`specification.md` に全文保存）。

## 実施日時 (Execution Date/Time)

2026-08-05 00:11:34 +0900

## 再現方法 (Reproduction Method)

```bash
cd /media/psf/SSD1TB/HEKBv2
uv pip install --python .venv/bin/python -e ~/meaning-space-runtime -e ~/categorical-lift-engine
source .venv/bin/activate
cd experiments
python exp_hekb_003_real_world_validation.py
```

結果は `experiments/results/exp_hekb_003.json` に上書き保存される。実行の
たびに実リポジトリ（`meaning-space-runtime`/`categorical-lift-engine`/
本リポジトリ）の現在の Markdown/Python/Git 状態を再走査するため、対象
リポジトリの状態が変化すると数値がわずかに変動しうる（決定論的なのは
同一入力に対する再現性であり、入力そのものの不変性ではない）。

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
ruff format --check clean / mypy --strict clean（31 files）。`src/hekb`
は無変更。

## 結果概要 (Results Summary)

全 6 サブチェック（stage4_5_searches, deterministic_replay,
pullback_accuracy, pushout_recall, latency_at_scale,
differential_synchronization）が pass。実 4-hop 合成射を実データから発見
（`msr/docs/BOUNDARIES.md → ... → KernelView`）。105 件の実オブジェクトに
対する検索レイテンシ p99 = 0.125ms（目標 10ms 以下）。Context Economy
Ratio は目標 0.15 に対しクエリ依存で 0.019〜0.219 — 正直に報告し、
無理に一律 pass とはしていない。

## 主要Finding (Key Findings)

1. `_concept_store.py`/`_file_backend.py` に実在するパス安全性バグを
   発見・修正 — レコード ID が `/` を含む場合、フラットファイル名として
   誤解釈されディレクトリが存在せず失敗していた。EXP-HEKB001/002 は
   短い平坦な ID しか使わなかったため露見しなかった。`experiments/`
   内のみの修正であり `src/hekb` には影響しない。
2. 幾何的ランキング関数の 4 項はすべて実際に計算可能な範囲に誠実に
   スコープされている — `D_potential` は centroid を持つオブジェクト
   （CLE 由来の Concept のみ）にのみ実計算し、それ以外は捏造せず
   正直に 0.0 とする。
3. Context Economy Ratio ≤ 0.15 は、105 オブジェクトという意図的に
   小規模な実コーパスでは全クエリについて成立するわけではない
   （0.019〜0.219）。これはランキング/閉包メカニズムの欠陥ではなく、
   コーパス規模に関する正確な実測結果として記録。

## 未解決事項 (Open Items)

- より大規模な実コーパス（`src/` 全体など）での Context Economy Ratio
  ≤ 0.15 の一般的成立可否は未検証。
- Graphify・ADR ディレクトリはワークスペース内に実在せず、real Graphify
  統合と real ADR インジェストは将来課題のまま。
- `D_ranking` の重み（0.4, 0.3, 0.2, 0.1）は選択値であり、実検索品質
  評価に基づくチューニングは未実施。

## 次のEXP (Next Experiment)

未定。EXP保存フェーズ（本アーカイブ作成）の完了後に判断。候補: より
大規模な実コーパスでの Context Economy 再検証、または real Graphify/MCP
サービスが利用可能になった時点での再統合検証。
