# Phase 0 DTS及び外部依存関係

## 1. 基準

2026年7月25日に、`taxonomy/tuple`、`taxonomy/oim/prototype`、
`taxonomy/experiments`及び`xBRL-GL2.0_btx`のXSD/XMLから`import`、`include`、
`linkbaseRef`、`schemaRef`及び`xsi:schemaLocation`を抽出しました。

| 検査項目 | 件数 |
| --- | ---: |
| dependency edge | 478 |
| external reference | 199 |
| local missing reference | 5 |
| XML parse error | 0 |

機械可読な全edgeは
[`inventory/dts-dependencies.csv`](inventory/dts-dependencies.csv)に記録します。

## 2. 公式XBRL GL package

### XBRL GL 2015

- status：Recommendation
- release／namespace date：`2015-03-25`
- package：`XBRL-GL-REC-2015-03-25.zip`
- modules：`gen`、`cor`、`bus`、`muc`、`usk`、`taf`、`srcd`
- palette：`plt/case-*`
- sample：`ids`

### XBRL GL 2017

- status：Public Working Draft
- work product name：XBRL Global Ledger 2017
- release／namespace date：`2016-12-01`
- package：`XBRL-GL-PWD-2016-12-01.zip`
- 2015 modulesに`ehm`を追加
- palette：EHMを含む`plt/case-*`を追加

公式packageのURLとSHA-256は
[`inventory/upstream-packages.csv`](inventory/upstream-packages.csv)を参照します。

## 3. 現在のTuple DTS

root候補は`taxonomy/tuple/gl/plt`のpalette schemaです。module schemaがconceptと
presentation linkbase参照を持ち、content schemaが同一namespaceのmodule schemaを
`include`し、依存moduleのcontent schemaを`import`する構造です。

現在のtreeは公式2017 PWDを基礎としますが、次を含むproject prototypeです。

- `cor` schema、presentation及び日本語labelの改変
- `ext`及び`jpn` module
- flattened palette
- `2026-MM-DD` placeholder
- 改訂vendor invoice sample

公式taxonomyを直接改変したものとして公開せず、今後は公式taxonomyのimport又は
project-owned namespaceでの再定義に切り分けます。

## 4. OIM/Palette dual-support DTS

normative conformance baselineは次の2 entry pointです。

- `taxonomy/oim/prototype/plt/plt-oim-2026-12-31.xsd`
- `taxonomy/oim/prototype/plt/plt-all-2026-12-31.xsd`

採用するassembly patternはADR-0003のとおりです。

1. module schemaがconceptを宣言し、presentation linkbaseを参照する。
2. content schemaが同一namespaceのmodule schemaを`include`し、依存content
   schemaを`import`する。
3. OIM paletteがroot content graphとmodule schemaへ到達可能にする。
4. label及びdefinition networkはentry pointからDTS reachabilityを持つ。
5. presentationをmodule経由で到達できる場合、paletteから重複参照しない。

XMLSpy及びArelleによるvalidityは確認済みです。ただし、semantic equivalence、
xBRL-CSV metadata、instance及びround tripは別の検査です。

## 5. 外部依存関係

抽出されたexternal reference 199件はすべて`www.xbrl.org`です。主な依存先は
次のとおりです。

- XBRL 2.1 instance schema
- XBRL linkbase schema
- XLink schema
- XBRL Dimensions schema
- XBRL Internationalの公式taxonomy namespace

release packageでは、外部taxonomyをproject packageへ混在させず、公式URLへの
参照とtaxonomy package catalogによるresolutionを使用します。

## 6. 欠落しているlocal reference

| source | reference | 処置 |
| --- | --- | --- |
| `taxonomy/tuple/gl/jpn/gl-jpn-2015-03-25.xsd` | `../gen/gl-gen-2015-03-25.xsd` | 2015 moduleとprototype dateを混在させない。jpn extensionの基準releaseを決めて再生成 |
| `taxonomy/experiments/codelists/shared/uncl_1001/...xsd` | `../../pool/uncl_1001/...xsd` | experimentは単独DTSではない。poolを取得recipeで解決するか、self-contained fixtureへ再構成 |
| `taxonomy/experiments/codelists/shared/uncl_5305/...xsd` | `../../pool/uncl_5305/...xsd` | 同上 |
| `taxonomy/experiments/document/document-oim-instance.xml` | `../gen/shared/uncl_1001/...xsd` | experiment間のpathをprofile manifestで解決 |
| `taxonomy/experiments/document/document-oim.xsd` | `../gen/shared/uncl_1001/...xsd` | 同上 |

これら5件は正式entry pointではなく、非完結の実験資産です。公開packageには含めず、
Phase 1のfixture分離で解消します。

## 7. UN/CEFACT依存

`source/unece`及び`taxonomy/experiments`は、UN/CEFACT CCL D25A、UNTDED、
UNTDID又はcode listを入力とする分析成果物です。D25Aというrelease identifierは
確認できますが、現在のCSVについて公式download file、取得日時及び元file
checksumを一意に復元できません。

したがって、これらはsemantic analysis用のprivate working inputとし、公開時には
次のいずれかを選択します。

1. 公式URL、release及びchecksumを記載したdownload recipeだけを提供する。
2. 書面による再配布・派生物公開許可を取得する。
3. UN unique IDとmappingだけを保持し、原文定義をpackageへ複製しない。

## 8. Consumer依存

providerはconsumer working treeを直接参照又は変更しません。UADC_PoC及び
LedgerExplorerのauthoritative LHM baselineは
[`inventory/consumer-lhm-baseline.csv`](inventory/consumer-lhm-baseline.csv)へ
checksumを固定し、移行時にはrelease packageとcrosswalkを介して連携します。
