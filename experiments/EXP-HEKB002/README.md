# EXP-HEKB002: Epistemic Storage, Semantic Closure Query & Knowledge Reuse Validation

## 目的 (Purpose)

観測 → Meaning Mapper → MSR/NVS-Kernel → CLE → HEKB Storage → Semantic
Closure Query → MCP → MSR 再注入という一気通貫の閉環パイプラインを、実際の
（フィクスチャではない）`meaning-space-runtime`/`categorical-lift-engine`
本番コードを用いて end-to-end で検証すること。

## 対象Repository (Target Repository)

`/media/psf/SSD1TB/HEKBv2`（主対象）。実行時に `meaning-space-runtime` と
`categorical-lift-engine` を editable install（experiments 専用の gate
dependency）として利用。

## 対象Commit (Target Commit)

`1799c321c66a92958b524fec9a8562e5f7c466ce`
`feat(hekb): implement EXP-HEKB002 semantic closure and closed-loop validation`

## 対象RFC (Target Specification)

EXP-HEKB002 v2.0.0（`specification.md` に全文保存）。

## 実施日時 (Execution Date/Time)

2026-08-04 23:41:35 +0900

## 再現方法 (Reproduction Method)

```bash
cd /media/psf/SSD1TB/HEKBv2
uv pip install --python .venv/bin/python -e ~/meaning-space-runtime -e ~/categorical-lift-engine
source .venv/bin/activate
cd experiments
python exp_hekb_002_closed_loop.py
```

結果は `experiments/results/exp_hekb_002.json` に上書き保存される。

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

全 5 サブチェック（persistence, dual_source_alignment, semantic_closure,
mcp_query, closed_loop_reuse）が pass。End-to-end yield 100%（例外 0件）。
MCP クエリレイテンシ p99 = 0.041ms（目標 5ms 以下）。ディスクから再ロード
した `Concept` を実 `msr.adapters.hekb.field_prior_from_concepts` で新規
`FieldPrior` に再注入し、摂動を与えた観測が実際に正しい basin へ再収束
することを証明（Basin Recovery）。

## 主要Finding (Key Findings)

1. `cle.abi.outputs.Concept` と `hekb.models.Concept` の間には変換
   アダプタが存在しなかった — 新規にリファレンスブリッジとして構築。
   幾何フィールド（centroid/hessian/invariants）は両 ABI で同一形状の
   ため非破壊で転送可能。
2. Graphify フィクスチャの初期版に、同一事実を双方向のエッジとして
   エンコードしたことによる 2-サイクルのバグが存在 — HEKB のバグでは
   なくフィクスチャのバグとして修正。`_semantic_closure.py` には
   サイクルガードを恒久的に保持。
3. 仕様スキーマの `homotopy_hash`/`betti_numbers` は実装せず省略
   （CLE はホモトピーアルゴリズムを実装していないため、捏造データを
   避けた）。実 `content_sha256` で代替。

## 未解決事項 (Open Items)

- `StorageProfile` fidelity gap は EXP-HEKB001 から継続して未解決。
- `cle.abi.outputs.Concept -> hekb.models.Concept` アダプタを両リポジトリ
  で共有される正式な API にすべきか、各実験のリファレンスブリッジのまま
  にすべきかは未決定（Priority C）。
- MCP はインプロセスのリファレンス実装であり、実ネットワークサービス
  ではない。

## 次のEXP (Next Experiment)

EXP-HEKB003 — Real-World Cross-Domain Semantic Search, Morphism Algebra &
Semantic Closure Validation（フィクスチャを実データ — 実 Markdown/Python/
Git 履歴 — に置き換え、Semantic Search Engine と幾何的ランキング関数を
追加）。
