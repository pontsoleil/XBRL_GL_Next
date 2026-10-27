# Full HMD → Tavi taxonomy generator（4モデル・datatype追加対応候補）

## 目的・変更の境界

この文書は、既存の `hmd_to_tavi.py`（元 SHA-256 `6be8b3e35bfdea6ce3683b065cf308154db89dd9de2c23ccaa0f9e75a1953714`）を基礎とする、4つの独立したHMD rootへの対応候補を説明する。対象は **Tavi taxonomy JSONの生成のみ**。インスタンス、Table Template、Viewerの生成・検証を追加しない。

対象rootは次のとおり。

| モデル | HMD root | 付加的なmodule |
| --- | --- | --- |
| COR | `cor:accountingEntries` | なし |
| COR-JPN | `jpn:accountingEntries` | `jpn` |
| BTX | `btx:businessTransactions` | `btx` |
| BTX-PINT | `pint:businessTransactions` | `btx`, `pint` |

各HMDは独立したタクソノミとして処理する。モデル間の意味定義・構造一致は要求しない。

## 改訂範囲

- HMDの18列 `value_domain` 契約と既存CLIの `--hmd`、`--output`、`--version`、`--include-documentation`、`--documentation-target` を保持する。
- 単一root必須とし、rootの`module`・`local_name`をHMDのC行から識別する。従来の `cor:accountingEntries` 固定条件を外す。
- 使用された追加moduleを `https://www.xbrl.or.jp/taxonomy/xbrl-gl-next/{module}` により解決する。従来のnamespace集合・順序は保持し、未登録moduleのみHMD出現順に追加する。
- taxonomy名とnetwork名をrootのmodule/local_nameから作成する。CORの既存名・frameworkName・namespace辞書の順序は維持する。
- HMDの `semantic_path`、`local_name`、`datatype`、`multiplicity`、`value_domain`、定義、行順は変更しない。既存のC/A/R処理とdocumentation labels出力を変更しない。
- BTX-PINTで新たに出現した4つのsemantic representation termについて、既存Part 1で確認された対応に基づき `BASE_TYPES` に限って追加する（次表）。

| HMD `datatype` | Tavi `baseType` | 根拠 |
| --- | --- | --- |
| `Identifier` | `xs:string` | Part 1 5.4.4 の確認済みIdentifier binding |
| `Code` | `xs:token` | Part 1 5.4.4 の確認済みCode binding |
| `Text` | `xs:string` | Part 1 5.4.4 の確認済みText binding |
| `Amount` | `xbrli:monetary` | Part 1のAmount monetary item binding、および旧 `Monetary` のTavi表現 |

`BASE_TYPES` のこの4件以外にdatatype対応を追加・変更しない。未知のdatatypeは従来どおり明示エラーとする。`value_domain`の解決方法、EE1、その他のBinding規則を変更するものではない。4件の型対応はWeb版の改訂候補であり、今回の正式HMDによる生成およびArelleでの受入判定はCodex実行結果を要する。

## 必要な入力

- 対象モデルの正式な **18列 HMD for taxonomy CSV** を1件ずつ指定する。Reviewed LHMや候補LHMを直接入力にしない。
- HMDのrootおよび各moduleは承認済み上流定義と照合する。単一rootでない入力は受理しない。
- Python 3.10以上・標準ライブラリ。出力ファイルが既に存在する場合、上書きせず停止する。

## 実行例（リポジトリのルートで）

以下はコマンドの形を示す例であり、`${HMD_COR}` 等は実在する受入済みHMD CSVへのパスに置換する。PowerShellの場合は環境に合った変数記法を用いる。正確なHMDパスとSHA-256はCodexが現行Candidateから記録する。

```bash
python -B tavi-poc/tools/hmd_to_tavi.py --hmd "$HMD_COR" --output "$TASK_OUTPUT/COR/taxonomy.json" --version 2026-10-26-candidate --include-documentation
python -B tavi-poc/tools/hmd_to_tavi.py --hmd "$HMD_COR_JPN" --output "$TASK_OUTPUT/COR-JPN/taxonomy.json" --version 2026-10-26-candidate --include-documentation
python -B tavi-poc/tools/hmd_to_tavi.py --hmd "$HMD_BTX" --output "$TASK_OUTPUT/BTX/taxonomy.json" --version 2026-10-26-candidate --include-documentation
python -B tavi-poc/tools/hmd_to_tavi.py --hmd "$HMD_PINT" --output "$TASK_OUTPUT/PINT/taxonomy.json" --version 2026-10-26-candidate --include-documentation
```

生成器は`--output`で指定したパスの親ディレクトリを作成する。既存の成果物を上書きしない。

## 非回帰・受入の扱い

- 元スクリプトのCOR生成内容との一致を確認する。原版対応HMD・versionを指定した場合の既存受入JSONとの一致は、既存基準・適用authorityに従ってCodexが確認する。
- 4モデルについて、生成されたTavi taxonomy JSONを既存のArelle OimTaxonomy環境で検証する。旧受入実績を今回の実行PASSとみなさない。
- `verify_hmd_to_tavi.py` は旧401行の3セル変更とラベル数を固定した専用検証器であるため、4モデルの共通検証器として流用しない。既存ファイルは無変更とする。
- 作業はWORK Candidateと検証・報告の範囲。Canonical登録・Official GIT反映・commit・pushは別の承認工程による。
- スクリプト改訂後に追加の不適合が判明した場合、Codexはコードを独自改訂せず、実行条件・エラーメッセージ・対象を報告する。

## 状態

前候補ではCOR、COR-JPN、BTXの生成とArelle error 0／warning 0がCodexから報告された。BTX-PINTだけは `Unsupported datatype: Identifier` で停止したため、Web版が上表の4型に限って改訂した。改訂後候補のBTX-PINT生成・Arelle検証・第三者clone再現は未実施であり、正式受入前。
