[English](README.md) | **日本語**

# XBRL GL Next サンプルタクソノミ

このディレクトリには、taxonomy version `2026-12-31` のXBRL GL Nextサンプルタクソノミパッケージを格納しています。

`2026-12-31`は、XBRL GL Nextを2026年中に完成しtaxonomyを公開する現在のプロジェクト計画を反映した予定version dateです。public releaseが既に承認済みであることを意味しません。

`../semantic-model/LHM_for_taxonomy/`配下のformal HMDを入力として、`../tools/taxonomy/xBRLGL_TaxonomyGenerator.py`により決定論的に生成されます。同じreviewed semantic modelについて、XBRL 2.1 TupleとOIM-compatibleの両方の実現を含みます。

## パッケージ概要

```text
taxonomy/
├─ gen/
│  └─ gl-gen-2026-12-31.xsd
├─ btx/
├─ bus/
├─ cor/
├─ lnk/
├─ taf/
├─ tuple/
│  ├─ cor_accountingEntries/
│  └─ btx_businessTransactions/
└─ oim/
   ├─ cor_accountingEntries/
   └─ btx_businessTransactions/
```

正式な生成taxonomy packageは**76ファイル**です。`README.md`および`README_ja.md`などのrepository説明文書は、この76ファイルには含めません。

## Module-level palette components

現在の各module directory（`btx`, `bus`, `cor`, `ehm`, `lnk`, `muc`, `taf`）には、TupleとOIMの両bindingで共用する再利用可能なmodule-level palette componentsがあります。

```text
<module>-2026-12-31.xsd
<module>-pre-2026-12-31.xml
label/<module>-lab-en-2026-12-31.xml
label/<module>-lab-ja-2026-12-31.xml
```

これらは、再利用可能なtaxonomy concept、label、presentation relationshipを提供します。同じsemantic moduleをTupleとOIMの両bindingで使用し、binding-specificな構造はそれぞれのbindingに応じて組み立てます。

## Tuple entry point

Tuple DTSを利用する場合は、次のいずれかをentry pointとします。

```text
tuple/cor_accountingEntries/cor-all-2026-12-31.xsd
tuple/btx_businessTransactions/btx-all-2026-12-31.xsd
```

HMD-specific `*-content-2026-12-31.xsd`が、選択したTuple DTSに必要な有効なstructural ComplexTypeを提供します。module schemaはpalette componentであり、それ単独がvalidation boundaryではありません。HMD-specific Tuple entry pointから検証してください。

## OIM entry point

OIM taxonomyは次のいずれかをentry pointとします。

```text
oim/cor_accountingEntries/cor-all-oim-2026-12-31.xsd
oim/btx_businessTransactions/btx-all-oim-2026-12-31.xsd
```

対応するdimensional definition linkbase:

```text
oim/cor_accountingEntries/cor-all-dim-2026-12-31.xml
oim/btx_businessTransactions/btx-all-dim-2026-12-31.xml
```

OIM bindingでは、Class occurrence scopeをprimary item、closed hypercube、typed dimensionによって表現します。OIM DTSからTuple content schemaはdiscoverされません。

## タクソノミの使い方

閲覧・検証では、個別のmodule schemaではなく、上記4件のHMD-specific entry pointのいずれかから開始してください。各bindingの使用例は[`../ids/`](../ids/)にあります。

repository rootから再生成する場合:

```text
py tools/taxonomy/xBRLGL_TaxonomyGenerator.py semantic-model/LHM_for_taxonomy \
  -b <empty-output-directory> \
  -n http://www.xbrl.org/int/gl/plt/2026-12-31
```

## 検証baseline

2026-08-14の受入baseline:

- formal generated taxonomy files: 76
- local references checked: 6,011
- unresolved local files: 0
- unresolved local fragments: 0
- dimensional locators checked: 1,437
- static package-checker failures: 0
- Arelle 2.44.1 taxonomy entry points: 4/4、error 0 / warning 0
- XMLSpy GUI: Tuple / OIM DTS確認済み

static checker:

```text
py tests/check_generated_package.py taxonomy
```

## 編集方針

このディレクトリには生成済みtaxonomy成果物を格納しています。通常の保守作業として生成taxonomy fileを手修正しないでください。変更が必要な場合は、reviewed semantic model、formal HMD、またはtaxonomy generatorに原因を反映し、決定論的に再生成して検証します。
