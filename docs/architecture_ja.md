[English](architecture.md) | **日本語**

# Architecture baseline

## 1. Semantic pipeline

本プロジェクトは、一つのsemantic sourceと二つのsyntax bindingを使用します。

```text
UN/CEFACT CCL and existing XBRL GL
                 |
                 v
       Foundational Semantic Model (FSM)
          Shared / Aligned / Distinct
                 |
          specialization by profile
                 v
        Business Semantic Model (BSM)
                 |
              graph walk
                 v
 Logical Hierarchical Model / HMD (LHM)
           /                     \
          v                       v
 XBRL 2.1 Tuple binding     OIM dimensional binding
                                  |
                                  v
                              xBRL-CSV
```

FSM、BSM及びLHMはsemantic artifactです。XSD、linkbase、JSON metadata及びCSV
tableはsyntax artifactです。serializationが変わるだけでconceptの意味を変えては
なりません。

### FSM superclass specialization

FSMで定義されたsuperclassは、そのchild ClassをFSMで定義することにより特殊化・
拡張します。child Classはsuperclass propertyを基礎としてpropertyを削除、変更又は
追加できます。

Class identityは`(module, class_term)`、参照先Class identityは
`(associated_module, associated_class)`、Association property identityは
`(property_term, associated_module, associated_class)`です。Association kindと
multiplicityはidentity keyに含めず、child Classで変更できます。

管理文字列にはXML Schema `token`相当の`whiteSpace="collapse"`を適用し、自由記述
definitionは改行と内部空白を保持します。collapse後、`module`及び
`associated_module`のASCII大文字だけを小文字化し、他のidentifierは大小文字を区別
します。両module列は論理module identifierです。QName形式のsemantic name又はClass
参照は入力エラーであり、QName、prefix及びnamespace URIはsyntax bindingだけで扱います。
空roleは推測せず空のまま保持します。

同一Class内では、Association kind、property ID又はsequenceにかかわらず、
`(association role, associated module, associated class)` keyを一度だけ定義できます。
重複はspecialization前に検出する入力エラーであり、ID又は入力順で候補を選択しません。
PoCではmodel errorにより全処理を停止せず、曖昧でないClassとpropertyをBSMへ出力し、
曖昧propertyを未反映／要確認としてreportします。BSMとdiagnostic reportを一組の
PoC結果として扱います。

Association及びSpecialization行は、同一module内参照でも`associated_module`と
`associated_class`を必須とします。欠落又は未知の参照はmodel errorです。他の処理を
継続できても、無効AssociationはBSMへ反映しません。

child ClassのFSM行でmultiplicity `0`を指定すると、一致する継承propertyの削除指示と
なります。削除property及び指示行自体は、有効child BSM、LHM又はtaxonomyへ出力
しません。一致するsuper propertyのない新規Associationで`0`又は`0..0`を指定した
場合も有効propertyとして出力しません。

入力fileを読めない、構文をparseできない、Class又はproperty識別に必要な列がない、
出力先へ書けない、又は既存file破損のおそれがある場合は致命的な入力level failure
です。その他のmodule、論理Class参照及びAssociationの曖昧性はmodel errorとして
隔離し、影響のないClassの処理を継続します。

### Canonical semantic tables

BSM semantic coreはFSM 14列の末尾に`id`だけを追加した15列で、`element`列を持ちません。
WORK固有のprovenance、external reference、context及びpresentation項目は、責務別
extension又はsidecarで管理します。

model errorを含むPoC BSMを正常成果物として表示しません。manifestに
`processing_status`、`error_count`、`warning_count`及び`report_file`を記録し、
diagnostic reportにproperty level詳細を記録します。任意のstatus sidecarで行level
dispositionを管理できますが、15列semantic coreへ追加しません。

Graph Walkは一つ以上のroot Classからlogical hierarchy tableであるLHMを生成します。
HMDはbinding段階でLHMから選択するメッセージ単位の部分集合であり、別semantic model
又は別Graph Walk生成物ではありません。選択HMDはLHM行の17列内容を変更しません。
単一root LHMは、そのrootのHMDと内容上同一です。契約は`path`、
`abbreviation_path`、`xpath`及び`associated_class`を除外し、`semantic_path`、
`associated_module`及び`class_term`を保持します。Reference traversalはR行と参照先PK由来の
`type=A, identifier=REF`行を出力し、RからREFへ参照先moduleを引き継いで探索を停止
します。REF名をparseして参照先を推測しません。XML配置はsyntax bindingの責務です。

Graph Walkはsemantic path確定後に`element`を生成します。末端名のLC3を初期候補とし、
必要ならparentからancestorの非重複語を前置してmodel全体で一意にします。比較では
大小文字を区別せず、空白とCamelCaseを語境界として扱います。全ancestor語でも一意に
ならない場合、自動連番を追加せず生成を失敗させます。

DNM出力及びGraph Walkの`-o` optionはtarget architectureに含めません。

14列FSM、15列BSM及び17列LHM契約はtaxonomy version `2026-12-31`から適用し、
manifestのcontract name及びversionで識別します。

## 2. Governance layers

### Shared

国、法制度、業界及び実装を越えて利用される世界共通の標準概念及び構造です。
国際標準又はUN/CEFACT CCL由来であるだけではSharedにならず、幅広い領域での利用が
必要です。Invoice、Shipment及びCustomsはShared root Classとなり得ますが、その配下の
ASBIE／BBIEのうち真に分野横断的なものだけをSharedとします。Shared entryは
syntax-neutral identifier、definition、datatype／representation term及びsemantic
pathを持ち、変更にはcentral reviewと強い互換性規則を適用します。

### Aligned

地域標準、国家標準、法令、規制又は公開された業界標準との整合を維持する標準定義です。
国際標準又はCCLのcomponentでも、用途が特定分野に限定されるものはAlignedとします。
upstream identifier及びreleaseへの明示provenance／mappingを保持し、profileにより
選択します。すべてのinstanceへ自動的に含めません。

### Distinct

企業、企業系列、製品、個別取引関係又はその他の閉じた共同体に固有の定義です。
公的な法令、規制、国家・地域標準又は公開業界標準はDistinctではなくAlignedに置きます。

## 3. Module responsibilities

初期baselineでは次の責務分割を使用します。module decision recordがacceptedとなる
までは名称を暫定とします。

| Module | Responsibility |
| --- | --- |
| `cor` | ledger／document envelope及び安定したaccounting core |
| `bus` | 再利用可能なbusiness party、address、contact及びmeasurable structure |
| `muc` | multicurrency structure |
| `taf` | tax structure |
| `ehm` | enhanced measurement structure |
| `usk` | 互換性のため保持するUS GAAP／accounting固有structure |
| `btx` | source business transaction及びtransaction document |
| `sta` | statistical observation、measure及びclassification |
| `lnk` | transaction、ledger entry、evidence及びreport間link |
| `gen` | generic datatype及びrepresentation term |
| `plt` | profile／palette entry point及びsyntax assembly |

`btx`、`sta`及び`lnk`をdumping groundとして扱いません。Sharedの再利用可能componentは
shared semantic libraryへ置き、moduleはdomain root、constraint及びprofile assemblyを
担当します。

## 4. OIM realization

Tuple containmentはOIMで明示dimension及びdefinition linkbase relationとして表現します。
各repeated Class levelには適切なtyped又はexplicit dimensionを割り当てます。
parent-child navigation、primary itemとhypercubeのattach、closed／open動作及びdefaultは
CSV行順から推測せず明示します。

対応する各profileは次を提供します。

- taxonomy entry point
- module及びroot選択
- cube及びhierarchyを定義するdefinition linkbase
- xBRL-CSV JSON metadata及びtable template
- semantic pathからconcept及びdimensionへのmapping
- positive及びnegative conformance example

## 5. Compatibility

2015／2017 Tuple taxonomyからの移行は、機械可読mapping tableで管理します。各旧concept
又はtuple pathを`unchanged`、`renamed`、`moved`、`split`、`merged`、
`deprecated`又は`unsupported`に分類します。互換性はrepository全体ではなくprofile
単位で表明します。
