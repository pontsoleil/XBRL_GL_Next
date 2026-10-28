[English](README_Tavi_4models_datatypes_candidate.md) | **日本語**

# HMD→Tavi taxonomy生成器：4モデル

現行の[`hmd_to_tavi.py`](../../tavi-poc/tools/hmd_to_tavi.py)は、受入済みの18列HMD CSVを1件読み込み、独立したTavi taxonomy JSONを1件生成します。Python 3.10以降の標準ライブラリを使用します。インスタンス、Table Template、Viewerの生成や、Specialisation・Graph Walkは行いません。


この生成器は、`taxonomy/tavi/` の4モデルのための正式HMD入力からTaviタクソノミを生成するものです。`tavi-poc/` のSimple／HMD Viewの独立した試作入力・生成工程とは区別します。共通Viewから3形式のインスタンスを生成する統一工程は今後の対象です。

## 公開モデル

| モデル | HMD root | HMD入力 | taxonomy JSON |
| --- | --- | --- | --- |
| COR | `cor:accountingEntries` | [`accounting-entries`](../../semantic-model/HMD/accounting-entries/XBRL_GL_Next_HMD_AccountingEntries_for_taxonomy.csv) | [`taxonomy.json`](../../taxonomy/tavi/accounting-entries/taxonomy.json) |
| COR-JPN | `jpn:accountingEntries` | [`accounting-entries-jpn`](../../semantic-model/HMD/accounting-entries-jpn/XBRL_GL_Next_HMD_AccountingEntries_for_taxonomy.csv) | [`taxonomy.json`](../../taxonomy/tavi/accounting-entries-jpn/taxonomy.json) |
| BTX | `btx:businessTransactions` | [`business-transactions`](../../semantic-model/HMD/business-transactions/XBRL_GL_Next_HMD_BusinessTransactions_for_taxonomy.csv) | [`taxonomy.json`](../../taxonomy/tavi/business-transactions/taxonomy.json) |
| BTX-PINT | `pint:businessTransactions` | [`business-transactions-pint`](../../semantic-model/HMD/business-transactions-pint/XBRL_GL_Next_HMD_BusinessTransactions_for_taxonomy.csv) | [`taxonomy.json`](../../taxonomy/tavi/business-transactions-pint/taxonomy.json) |

4モデルは個別に生成します。root間で構造・型が同一であることは要求しません。入力は`value_domain`を含む正式な18列HMDであり、Reviewed LHMではありません。

## 入出力と型

コマンドには`--hmd PATH`、`--output PATH`、`--version TEXT`、`--include-documentation`、任意の`--documentation-target QName`を指定できます。既存出力は上書きしません。HMDのsemantic path、module、行順、利用可能なlabel・documentationを保持し、未対応datatypeや不正rootは拒否します。

対応するTavi base typeには、`Identifier` → `xs:string`、`Code` → `xs:token`、`Text` → `xs:string`、`Amount` → `xbrli:monetary`が含まれます。moduleのnamespaceは`https://www.xbrl.or.jp/taxonomy/xbrl-gl-next/{module}`形式です。

正確なコマンド、入力版、検証範囲、実行環境は[4モデル再現ガイド](../../tavi-poc/README_REPRODUCE_4_MODELS.md)を参照してください。記載された過去の実行証跡は、新たなclone環境での検証結果を意味しません。
