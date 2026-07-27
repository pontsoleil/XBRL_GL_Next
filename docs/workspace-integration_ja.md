[English](workspace-integration.md) | **日本語**

# Workspace統合

## 目的と状態

XBRL GL Nextは、version付きsemantic model及びOIM taxonomy packageのproviderに
なることを想定しています。他のrepositoryはconsumerです。consumer repository及び
そのデータは、この登録候補には含めません。

以下のprovider release package、release manifest、consumer adapter及び本番切替は
**計画中**かつ**未登録**です。consumerは開発者のworking tree内のpathへ依存しては
なりません。

## 確認済みconsumer候補

### UADC_PoC

ローカル調査で、EN 16931 invoice LHM及び関連OIM生成を取引文書移行pilot候補として
確認しました。これは別consumer repositoryに関する観察であり、登録、所有、承認又は
現時点の互換性を主張するものではありません。

### LedgerExplorer

ローカル調査で、会計、販売及び購買LHM profileをledger／subledger移行pilot候補
として確認しました。これも別consumer repositoryであり、provider packageには
含めません。

## 計画中のprovider release契約

将来のconsumerは、隣接working treeのpathではなく、固定されたversion付きpackageを
統合します。次の構成は例示であり、現在は登録されていません。

```text
release/
  manifest.json
  model/
    semantic-model.csv
    profile-lhm.csv
  taxonomy/
    catalog.xml
    entrypoints.json
  mappings/
    tuple-to-semantic.csv
    consumer-to-semantic.csv
  examples/
  validation/
    report.json
```

計画中のmanifestは、semantic model契約、profile、namespace date、entry point、
source commit、file hash、互換性level及びvalidation状態を識別します。manifest
schemaは、別途登録・検証されるまで利用可能として扱いません。

## 安定した統合key

現行設計では次のkeyを評価します。

1. `semantic_id` — 現行ドラフト契約が保持するsyntax-neutral identity
2. `semantic_path` — profile内の人が読める論理path
3. `concept_qname` — syntax bindingの出力
4. `legacy_identifier` — 移行専用consumer identifier

CSV列位置、生成行sequence、QName prefix及びローカルfilesystem pathはsemantic
identityではありません。`semantic_id`の将来の扱いは、承認済みsemantic-model
契約に従います。

## 移行段階

### Stage A — 棚卸しと凍結

consumerの動作を変更せず、各consumer model、binding、設定package、生成taxonomy、
test command及びSHA-256を記録します。

### Stage B — 明示crosswalk

[`../contracts/consumer-mapping-template.csv`](../contracts/consumer-mapping-template.csv)
を使用し、各行を`equivalent`、`rename`、`move`、`split`、`merge`、
`extension`、`deprecated`又は`unmapped`に分類します。未reviewの曖昧一致を
使用しません。

commitするtemplateは空のままです。記入済みmappingにはconsumer identifierが
含まれる可能性があるため、登録前にprivacy、confidentiality、license及び共有範囲を
別途reviewします。

### Stage C — Shadow generation

固定したlegacy packageとprovider profile候補の両方からconsumer出力を生成します。
semantic fact、繰返し行scope、datatype、unit、cardinality及びentry pointを比較します。

### Stage D — Consumer adapter

version付きprovider packageを解決します。開発時には
`XBRL_GL_NEXT_PACKAGE`のような環境変数でlocal packageを指定できますが、本番及び
CIは固定package又はfixtureを使用します。

### Stage E — 切替

positive、negative及びround-trip test合格後だけ切り替えます。少なくとも一移行cycle、
固定したrollback packageを保持します。

### Stage F — 廃止

authority、ownership、release及びrollback責任がproviderへ移った後だけ、
project-local model generatorを廃止します。consumer固有syntax bindingはconsumer
repositoryに残します。

## 互換性gate

- すべてのlegacy行に明示的なmapping dispositionがある
- semantic identityを異なるdefinitionへ再利用しない
- repeated-Class scopeが同等のfact groupingを生成する
- datatype、unit、nil動作及びcardinalityが同一又は意図的に移行済み
- source round tripがbindingされたすべての値を保持する
- OIM metadataが登録済みtaxonomy entry pointを解決する
- 独立processorがpackageをvalidateする
- consumer testが固定provider versionに対して合格する
- package及びmappingに認証情報、実取引、未承認個人情報又は機密設定がない

## 所有、ライセンス及び分離

プロジェクト作成文及び空templateには、project documentation licenseを適用できます。
外部model、標準、consumer file及び派生taxonomyには各権利者の条件が残り、再ライセンス
しません。権利未解決資料はPrivate repositoryにも登録しません。

providerはconsumer repositoryへ直接書き込みません。開発者固有のWindows pathでは
なく、repository role、環境変数及びrepository相対pathを使用します。
