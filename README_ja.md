[English](README.md) | **日本語**

# XBRL GL Next

## 目的

このリポジトリには、XBRL GL Next Taxonomy Framework、正規のセマンティックモデル・パイプライン、用途別HMDパレット、生成済みTuple／OIMサンプルタクソノミ、サンプルインスタンス、再現・検証のためのツールとテスト、およびTavi PoCを収録しています。

COR、BTX、AAAは再利用可能な意味定義を備えた**絵具箱（semantic paint boxes）**であり、用途別HMDは必要な意味を選択・構成する**パレット**です。共通の意味モデルに基づき、XBRL 2.1 Tuple、OIM、Taviという異なるタクソノミ実現方式を検討しています。実装・受入状況は方式ごとに区別します。

## 状態

現在のリポジトリのパッケージは共同レビュー用です。**正式な公開版、標準、またはいかなる組織の公式見解としても承認されていません。**

正規のプロジェクト・モジュール名前空間は `https://www.xbrl.or.jp/taxonomy/xbrl-gl-next/{module}` です。予定するタクソノミの版日付 `2026-12-31` は物理ファイル名のみに含まれ、名前空間URIには含まれません。この日付は正式公開の承認を意味しません。

来歴とライセンス上の境界は [THIRD_PARTY_NOTICES_ja.md](THIRD_PARTY_NOTICES_ja.md) を参照してください。

## プロジェクトの段階

以下はプロジェクト全体のレビュー・公開ライフサイクルであり、**Tavi PoC固有のPhase 1／2とは別**です。

### Phase 1 — 再現可能なサンプルパッケージ

共同レビュー用に整理した最初の再現可能なXBRL GL Nextサンプルパッケージです。次を含みます。

- Requirements Specificationおよび当初の受入済みサンプルパッケージに対応するTaxonomy Framework Part 1〜4
- FSM → BSM → LHM → HMD-for-taxonomyの意味モデル処理
- 生成済みTuple／OIMパレットタクソノミ
- Tuple／OIMサンプルインスタンス
- パッケージの再現・検証に必要な正規ツールとテスト

後から追加されたPart 5とTavi PoCは、過去のTuple／OIM検証の受入範囲を遡って拡張するものではありません。Phase 1は共同レビュー用であり、正式公開の承認を意味しません。

### Phase 2 — 外部共同レビュー

Phase 1の成果物を基礎に、XBRLコミュニティその他の関係者とレビュー・調整する段階です。主な論点は次のとおりです。

- セマンティックモデルのアーキテクチャ
- Specialisation、Graph Walk、LHM／HMDの処理モデル
- Tuple／OIMタクソノミのバインディング
- Extension方式とAligned Pool
- 実装の再現性と検証

Part 5とTavi PoCは、別途対象範囲を明示したレビュー資料として追加されています。

### Phase 3 — 公開候補版

外部レビュー結果を反映し、Framework、タクソノミパッケージ、版管理、名前空間、ライセンス、公開手続を整理して公開候補版を準備します。

### Phase 4 — 正式公開と保守

正式公開とその後の版更新、拡張、Aligned Poolの保守および適合性関連の更新を想定します。

## Framework文書

[`TaxonomyFramework/`](TaxonomyFramework/) にはRequirements Specification、Taxonomy Framework Part 1〜5、および登録済みサンプル成果物のinventoryがあります。

- **Part 1 — General rules：** シリアライゼーション非依存の意味モデル処理と正式HMDの契約
- **Part 2 — Tuple palette taxonomy：** 正式HMDからのXBRL 2.1 Tuple実現
- **Part 3 — OIM palette taxonomy：** 正式HMDからのOIM実現
- **Part 4 — Aligned Pool and extension governance：** 意味拡張の分類、整合、登録、公開の管理
- **Part 5 — Tavi palette taxonomy：** 用途別HMDビューとTaviタクソノミ／Table Templateの実現

Part 2、3、5はPart 1の共通意味基盤に基づく異なるタクソノミ実現方式です。拡張に関してはPart 4のガバナンスが適用されます。これは各実現方式の検証・公開状態が同じことを意味しません。

正式なFramework文書は英語で管理し、[`TaxonomyFramework/README_ja.md`](TaxonomyFramework/README_ja.md) で日本語の案内を提供します。

## 正規semantic pipeline

意味処理の順序は **FSM → BSM → Candidate LHM → Reviewed LHM → 正式HMD → タクソノミBinding** です。Candidate LHMからReviewed LHMへの移行には、管理された人による意味レビューが必要であり、Reviewed LHMを自動再生成で上書きしません。

公開済みFSM／BSMには `semantic-model/FSM/FSM.csv`、`semantic-model/FSM/FSM_btx.csv`、`semantic-model/BSM/BSM.csv` があります。Candidate／Reviewed LHMは `semantic-model/LHM/` 配下のroot別ディレクトリに配置され、Accounting EntriesとBusiness Transactionsには両CSVが存在します。Journal Entriesには、受入済みworkbookを意味上のauthorityとするReviewed CSVがあります。Accounting EntriesとBusiness Transactionsの正式HMDセットとmanifestは `semantic-model/LHM_for_taxonomy/` に、Journal Entriesの独立したHMDとmanifestは `semantic-model/HMD/journal-entries/` にあります。ファイルの存在・登録SHA一致だけで、現行構成の一括再生成や検証PASSを主張しないでください。実行前に対象rootの受入済み入力と証拠を確認してください。

## サンプルtaxonomyとinstance

公開taxonomyにはroot別の独立したDTSが3組あり、それぞれにTupleとOIMの入口があります（taxonomy入口は計6件。ただし6件のvalidation PASSを意味しません）。

- `taxonomy/accounting-entries/`：Accounting EntriesのTuple／OIM入口
- `taxonomy/business-transactions/`：Business TransactionsのTuple／OIM入口
- `taxonomy/journal-entries/`：Journal EntriesのTuple／OIM入口

`ids/tuple/`にはTupleサンプルインスタンス2件、`ids/oim/`には各JSONメタデータをレポート入口とするxBRL-CSVサンプル2件があります。サンプル数とtaxonomy入口数を混同しないでください。

## Tavi PoC — Structured Tidy Data Viewer

[Tavi PoC](tavi-poc/) では、同一のStructured Tidy Data CSVを2種類のTavi定義を用いて表示します。

- [Simple Tavi Viewer](https://pontsoleil.github.io/XBRL_GL_Next/tavi-inst.html)
- [HMD View Viewer](https://pontsoleil.github.io/XBRL_GL_Next/tavi-inst-hmd-view.html)

自己完結型のPhase 1 HTMLでは、左側のタブにTable TemplateとTaviタクソノミのJSONソースを、右側に転置したCSVを表示します。**Tavi PoC Phase 1**はプロジェクト全体のPhase 1とは別です。Tavi PoC Phase 2では、JavaScriptによるProperties連動表示を予定しています。Viewerは正式なXBRL／Tavi検証を行いません。個別のタクソノミファイルの公開状態などの詳細は[`tavi-poc/README.md`](tavi-poc/README.md)を参照してください。

## 正規ツール

次のツールは公開リポジトリ内で実在し、登録ファイルと一致しています。ただし、この一覧だけで現行テスト一式のPASSを示すものではありません。

- `tools/semantic/specialisation.py`
- `tools/semantic/graphwalk.py`
- `tools/semantic/post_graphwalk.py`
- `tools/semantic/validate_lhm.py`
- `tools/taxonomy/xBRLGL_TaxonomyGenerator.py`

最後のファイルが確認済みのTuple／OIM Taxonomy Generator実装です。`src/`への移行根拠はありません。実行前に対応するプログラム仕様・入力authority・受入証拠を確認してください。

## Taxonomy generation

公開されているGeneratorでは次のCLI構文を利用できます（実装上の確認であり、新たな実行PASSではありません）。

```text
python tools/taxonomy/xBRLGL_TaxonomyGenerator.py \
  --hmd-dir <HMD_DIRECTORY> \
  --output-dir <TAXONOMY_OUTPUT_DIRECTORY> \
  --namespace <NAMESPACE>
```

必須引数`--namespace`には、例えば `https://www.xbrl.or.jp/taxonomy/xbrl-gl-next/plt` の名前空間anchorを指定します。位置引数`lhm_for_taxonomy`と`-b`／`--base-dir`は後方互換のため利用できます。新しい自動処理では確認済みGeneratorの`--hmd-dir`と`--output-dir`を使用してください。

## 正規テストと検証

再現・受入に用いるテスト一覧は、受入済みinventoryと個々の実行証拠で確認してください。過去の検証記録には、Arelleの版数、入力セット、エントリーポイントの対象範囲が異なるものがあります。実行ID、入力SHA-256、入口一覧、検証結果の対応が確定するまで、**Phase 1のArelle検証baselineは確認中であり、本READMEでは単一の数値的な受入baselineを断定しません**。歴史的記録を現在の受入結果と読み替えず、実際に検証された構成に対応するinventoryと実行報告を参照してください。

## Repository tree

```text
TaxonomyFramework/  Requirements Specification、Framework文書、inventory
semantic-model/     FSM／BSMおよびroot別LHM／HMD
taxonomy/           Accounting Entries、Business Transactions、Journal EntriesのTuple／OIM DTS
ids/                Tuple／xBRL-CSVサンプルインスタンス
tavi-poc/           Tavi例、タクソノミ定義、静的HTML Viewer
tools/              公開済みsemantic toolsと確認済みTuple／OIM Generator（受入は対象別）
tests/              正規回帰テストとパッケージチェッカー
```
