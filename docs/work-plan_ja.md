[English](work-plan.md) | **日本語**

# 推奨作業計画

## Phase 0 — Repository及びprovenance baseline

- 状態：2026-07-25完了。
- target Git repositoryには現在、専用rearchitecture branchと`origin` remoteがある。
  repository ownership、visibility、publication authority及び各pushは、推測される
  許可ではなく明示的なgovernance gateとする。
- UADC_PoC及びLedgerExplorerのconsumer LHM checksumを
  `TaxonomyFramework/inventory/consumer-lhm-baseline.csv`で凍結した。
- XBRL GL 2015／2017 packageのURL、file count、checksum及びlicense statementを記録した。
- UN/CEFACT入力は、公式package checksum又は再配布許可を記録するまでprivate分析資料とする。
- Open Issueにはstable IDを付与し、ADRを`docs/decisions`に配置し、public release
  blockerを後続設計作業から分離した。
- 現行taxonomy fileはすべて`prototype`のままである。

Exit conditionは達成済みです。各import artifactについて、source又はsource分類、判明
しているversion、権利状態及びGitHub dispositionを記録しました。不明なauthorityを
暗黙の許可にせず、該当artifactをpublication holdとします。

## Phase 1 — 要件及びconformance matrix

- 各`GL-REQ-*`要件を機械可読requirement recordにする。
- 要件をFramework節、実装artifact及びtestへmappingする。
- `LHM`対`HMD`、`Shared`対`Aligned`及びprofile／palette用語を確定する。
- ledger、invoice／business transaction及びstatistical observationの初期profileを定義する。

Exit condition：すべてのprototype機能が承認済みrequirement及びprofileへtraceできること。

## Phase 2 — 2015／2017 reverse engineering

- entry point、module、tuple、type、substitution group及びlinkbaseを棚卸しする。
- canonical tuple path及びstable source identifierを作成する。
- semantic duplicate及びmodule couplingを特定する。
- `mapping/tuple-to-semantic.csv`を作成する。

Exit condition：保持する2015／2017 conceptごとに明示的なsemantic dispositionがあること。

## Phase 3 — Foundational Semantic Model

- name、definition、representation term、cardinality及びassociationを正規化する。
- Shared、Aligned及びDistinctのgovernance状態をalgorithmic similarity scoreから分離する。
- Shared候補へUN/CEFACT Dictionary Entry Name、unique ID、release及びbusiness contextを
  付与し、Aligned specialization作成時にも対応provenanceを保持する。
- XML QNameから独立したstable concept ID及びsemantic pathを割り当てる。
- Association property identity keyを
  `(property_term, associated_module, associated_class)`として決定的なsuperclass
  specializationを定義する。
- Classを`(module, class_term)`、参照先Classを
  `(associated_module, associated_class)`で識別する。同一module内でも両参照列を必須
  とする。管理文字列へXML Schema `token`相当の空白collapseを適用し、自由記述definition
  は保持する。module identifierのASCIIだけを小文字化する。QName形式semantic valueは
  分割せず拒否し、QName生成をsyntax bindingへ委ねる。空roleは空のまま保持する。
- 同一Class内の重複identity keyを、association kind、multiplicity、property ID又は
  sequenceにかかわらずspecialization前に報告する。
- PoCではmodel error後も影響のないClass及び曖昧でないpropertyを処理する。曖昧
  Associationを選択又は統合せず、未解決／要確認としてBSMとdiagnostic reportに記録する。
- child Classによる継承propertyの削除、変更及び追加を許可する。association kind及び
  multiplicityは変更可能でidentity keyに含めない。
- `cor`、`bus`、`btx`、`sta`、`lnk`及びsupporting moduleのownership規則を定める。

PoC exit condition：FSM validationが未解決Class、duplicate stable ID及び曖昧Associationを
すべて特定し、影響のない内容を決定的に出力し、各未反映項目をdiagnostic reportへ
関連付けること。clean releaseには未解決model error 0件が必要です。

## Phase 4 — Profile、BSM及びGraph Walk

- declarative profile manifestを定義する。
- Shared definitionを直接編集せず、child propertyの削除、変更及び追加によりFSMをBSMへ特殊化する。
- multiplicity `0`を削除指示とし、一致する継承property及び指示行を有効BSMへ出力しない。
  super propertyに一致しない新規Associationの`0`又は`0..0`も有効propertyとしない。
- 宣言済みroot及びassociation選択からLHM/HMDを決定的に生成する。
- Reference AssociationではR行及び参照先PK由来REF行を出力し、RからREFへtarget moduleを
  引き継ぎ、nameをparseせず探索を停止する。
- 14列FSMを読み、15列BSM semantic core及び17列LHM/HMD semantic coreを出力する。
  BSM `element`を除外し、LHM/HMDの`path`、`abbreviation_path`、`xpath`及び
  `associated_class`を除外する。`semantic_path`、`associated_module`及びHMD identity
  `class_term`を保持し、確定semantic pathからLHM/HMD `element`を生成する。
- parent／ancestorの非重複語を前置し、model全体で一意なLC3 element nameを生成する。
  ancestryで一意化できない場合、自動連番を付けずerrorとする。
- target CLI及びtest planからDNMとGraph Walk `-o`を除く。
- 各変換のchange reportを生成する。
- PoC結果状態を15列coreでなくmanifestへ記録する。model errorが残る場合は
  `processing_status=poc-with-errors`、件数及びdiagnostic-report参照を使用する。
- 三つの変換toolをCLI利用可能にし、固定fixtureでtestする。
- taxonomy version `2026-12-31`から新契約を適用し、manifest contract name／versionで
  legacy／new artifactを識別する。

Exit condition：clean checkoutから同一BSM及びLHMを再生成でき、multiplicity `0`で
削除したpropertyがBSM、LHM/HMD及び生成taxonomyに存在しないこと。

## Phase 5 — Dual syntax binding

- 互換参照としてTuple bindingを生成する。
- repeated Class及びparent-child levelのOIM cube patternを定義する。
- primary item、dimension、domain、default、closed／open動作及びtarget roleを定義する。
- 同じprofile manifestからJSON metadata及びCSV templateを生成する。
- tuple path ↔ semantic path ↔ OIM aspectの決定的mappingを追加する。

Exit condition：同等のTuple及びxBRL-CSV exampleが、手作業の解釈なしに同じsemantic
recordへmappingされること。

## Phase 6 — Domain pilot

広範なCCL import前に、次の小規模vertical sliceを実装します。

1. UADC_PoC EN 16931 vendor invoice
2. LedgerExplorer purchase orderからinvoice、ledgerへのlink
3. source transactionにlinkしたstatistical observation

各pilotにはsource message mapping、profile manifest、生成taxonomy、example、
validation rule及びround-trip比較を含めます。

Exit condition：三つのpilotがsemantic、XBRL及びOIM validationに合格すること。

consumer切替は`docs/workspace-integration_ja.md`に従います。providerはcrosswalk及び
shadow comparison完了前にconsumer LHMを上書きしません。

## Phase 7 — Governance及びpublication

- Shared core change process及びAligned registry reviewを確立する。
- namespace／version／deprecation policyを定義する。
- package manifest及びcatalog resolutionを公開する。
- XML Schema、linkbase、OIM metadata、CSV、mapping及び再現可能生成のCIを追加する。
- 権利及びconformance review後だけWorking Draft releaseを公開する。

Exit condition：tag付きpackageを再現でき、追跡可能で、独立にvalidateできること。
