# FSM／BSM／LHM列契約とbinding段階のHMD（Phase 1改訂案）

## 1. 位置付け

本書は、XBRL GL Nextのsemantic modelに`associated_module`を導入するための
実装前列契約案である。Semantic処理programはFSM 14列、BSM 15列及びLHM 17列へ
改定済みであるが、正規データ、binding、HMD、taxonomy generator及びconsumerは
継続確認中である。

列数を固定値から決めない。意味上必要な列を定義した結果として、FSM 14列、BSM
15列、LHM 17列を改訂案とする。BSMはFSMの14列に末尾`id`だけを追加する。
Graph Walkの生成物はLHMである。HMDはbinding段階で利用するLHMのメッセージ単位の
部分集合であり、別のSemantic処理生成物ではない。HMDの行はLHMの17列を内容変更せず
使用し、`path`、`abbreviation_path`、`xpath`及び`associated_class`を保持しない。

## 2. 文字列セルの共通入力前提

文字列列を管理文字列と自由記述に分ける。管理文字列にはXML Schemaの`token`型に
おける`whiteSpace="collapse"`と同じ空白処理を適用する。

| モデル | 管理文字列 |
|---|---|
| FSM／BSM | `property_type`, `identifier`, `module`, `class_term`, `property_term`, `representation_term`, `associated_module`, `associated_class`, `multiplicity`, `label_local`, `id` |
| LHM及びそのHMD部分集合 | `type`, `identifier`, `name`, `datatype`, `multiplicity`, `domain_name`, `module`, `class_term`, `associated_module`, `id`, `semantic_path`, `label_local`, `element` |

`definition`及び`definition_local`（`Documentation`、`LocalDocumentation`、
`local_definition`等の同等列を含む）は自由記述である。collapseを適用せず、原文の
改行及び内部空白をCSVの引用フィールドとして保持する。

`module`及び`associated_module`だけは、collapse後にASCII大文字を小文字へ変換する。
Unicode変換は行わない。小文字化後のmodule衝突は入力エラー又は移行時の要確認事項
とする。Class名、property termその他の識別子は大文字と小文字を区別する。

これ以外の全角・半角、単複、記号、略語、別名又は同義語の変換及び他セルからの
暗黙補完を行わない。

header aliasの照合だけは別の構文処理であり、headerの大文字・小文字、空白、
underscore及び句読点を正規化できる。header処理をデータセルの値へ適用しない。

## 3. Class及びAssociationの識別

所有Classの識別は次のとおりである。

```text
Class identity
= (module, class_term)
```

参照先Classの識別は次のとおりである。

```text
Referenced Class identity
= (associated_module, associated_class)
```

Association propertyの識別及びsuper classとchild classのAssociation照合は
次のとおりである。

```text
Association property identity
= (property_term, associated_module, associated_class)
```

`property_term`は空欄を許容する。空欄は空欄のままidentityの一要素として比較し、
`associated_class`、Class名、module、QName、ID又は入力順から推測又は生成しない。

`property_type`、`multiplicity`、property ID、FSM ID、`sequence`及び入力順は
Association property identityへ含めない。同じClass内で同じAssociation property
identityが複数あれば重複入力エラーとする。`associated_module`が異なれば、
`property_term`及び`associated_class`が同じでも別Associationである。

`module`及び`associated_module`は論理的なmodule識別子である。QName prefix、
XML namespace prefix又はnamespace URIではない。QName、prefix及びnamespace URIとの
対応はsyntax bindingで管理する。

FSM、BSM及びLHMの意味モデル名又はClass参照セルへQNameを単一値として記載しては
ならない。コロンをQName区切りとして含む値は入力エラーとし、自動分割、prefixから
module／namespaceへの変換、local nameだけの採用及び警告だけでの受理を禁止する。

## 4. 実ファイルと改訂列契約

### 4.1 確認した実ファイル

| モデル | 確認したファイル | データ行 | 改訂前列数 | 改訂前の列順 |
|---|---|---:|---:|---|
| FSM core | `source/models/core/xBRL-GL2.0_FSM.csv` | 632 | 13 | `seq`, `level`, `Property type`, `Identifier`, `Class`, `Property Term`, `BaseType`, `Associated Class`, `Multiplicity`, `Documentation`, `module`, `LocalLabel`, `LocalDocumentation` |
| FSM btx | `source/models/business-transactions/xBRL-GL2.0_FSM_btx.csv` | 359 | 13 | coreと同じ。ただし`Documentation`は`Definition` |
| BSM core | `source/models/core/xBRL-GL2.0_BSM.csv` | 435 | 15 | `sequence`, `level`, `property_type`, `identifier`, `class_term`, `property_term`, `representation_term`, `associated_class`, `multiplicity`, `definition`, `module`, `element`, `label_local`, `definition_local`, `id` |
| BSM btx | `source/models/business-transactions/xBRL-GL2.0_BSM_btx.csv` | 775 | 15 | coreと同じ |
| LHM core | `source/models/core/xBRL-GL2.0_LHM.csv` | 364 | 19 | `sequence`, `level`, `type`, `identifier`, `name`, `datatype`, `multiplicity`, `domain_name`, `definition`, `module`, `class_term`, `id`, `path`, `semantic_path`, `abbreviation_path`, `label_local`, `definition_local`, `element`, `xpath` |
| LHM btx | `source/models/business-transactions/xBRL-GL2.0_LHM_btx.csv` | 609 | 19 | coreと同じ |

既存LHMのR行では、`module`が参照先moduleを表す一方、`class_term`は所有Classを
表す例があり、所有側と参照側の意味が分離されていない。この混在は移行時に
明示的なmappingで解消し、列位置や値から推測しない。

### 4.2 改訂前後の概要

| モデル | 改訂前 | 改訂後案 | `associated_module`の位置 | 備考 |
|---|---:|---:|---|---|
| FSM | 13 | 14 | `representation_term`と`associated_class`の間 | 全列をcanonical nameへ揃える |
| BSM | 15 | 15 | `representation_term`と`associated_class`の間 | FSM 14列＋末尾`id`。`element`を削除 |
| LHM | 19 | 17 | 16番目 | `path`、`associated_class`、`abbreviation_path`及び`xpath`を除く。HMDはbinding時にこのLHMから選択する |

### 4.3 FSM canonical input：14列

```text
sequence
level
property_type
identifier
module
class_term
property_term
representation_term
associated_module
associated_class
multiplicity
definition
label_local
definition_local
```

実ファイルのheader aliasは次へ対応付ける。

| canonical name | 受理する代表header |
|---|---|
| `sequence` | `seq`, `sequence` |
| `level` | `level` |
| `property_type` | `Property type`, `property_type` |
| `identifier` | `Identifier`, `identifier` |
| `module` | `module`, `code` |
| `class_term` | `Class`, `Class Term`, `class_term` |
| `property_term` | `Property Term`, `property_term` |
| `representation_term` | `BaseType`, `Representation Term`, `representation_term` |
| `associated_module` | `Associated Module`, `associated_module` |
| `associated_class` | `Associated Class`, `associated_class` |
| `multiplicity` | `Multiplicity`, `mult`, `multiplicity` |
| `definition` | `Definition`, `Documentation`, `definition` |
| `label_local` | `LocalLabel`, `label_local` |
| `definition_local` | `LocalDocumentation`, `definition_local` |

### 4.4 BSM canonical semantic core：15列

```text
sequence
level
property_type
identifier
module
class_term
property_term
representation_term
associated_module
associated_class
multiplicity
definition
label_local
definition_local
id
```

BSMの先頭14列はFSMと同一であり、15列目に`id`だけを追加する。`element`は
Specializationで生成、保持又は更新しない。WORK固有のprovenance、inheritance、
external reference、context及びpresentation項目はこの15列へ混在させず、
責務別sidecarとmanifestで管理する。

### 4.5 LHM canonical semantic core：17列

```text
sequence
module
level
type
identifier
name
datatype
multiplicity
domain_name
definition
label_local
definition_local
element
id
semantic_path
associated_module
class_term
```

- `path`及び`abbreviation_path`は生成又は出力しない。
- `xpath`は意味モデルへ保持せず、syntax binding側で管理する。
- Reference AssociationはR行及び参照先Classの主キーから派生するREF行を出力して
  探索を停止する。REF行は`type=A`かつ`identifier=REF`である。
- Attribute及びREFのdatatypeを保持する。
- R行は参照先moduleを`associated_module`へ保持する。参照先ClassはBSMから解決した
  Graph Walk処理状態及び階層関係で管理し、LHMへ`associated_class`列を追加しない。
- R行の`name`はroleありなら`property_term + "_ " + associated_class`、空roleなら
  `associated_class`とし、QName prefixを含めない。
- REF行の`associated_module`は直前R行の参照先moduleを継承する。参照先はR行との
  階層及びGraph Walkの処理状態で追跡し、REF名又はQNameから再推測しない。
- 参照先Classが不正ならR行及び配下REF行を出力しない。
- `class_term`は各行の所属Classを表す。
- LHMはGraph Walkが一つ以上のroot Classから生成する論理階層表である。
- HMDはbinding段階でLHMから選択する一つのメッセージ又はroot Class単位の部分集合で
  あり、同じ17列の行を内容変更なしで使用する。
- BSMのroot Classを一つに限定してGraph Walkを実行したLHMは、そのroot Classに対応する
  HMDと行内容、列順及び行順が同一である。HMDとしての識別情報、profile及びtarget
  syntaxとの対応はbinding manifest又はsidecarで付与し、LHM行へ混在させない。
- 旧LHM行数又は列位置へ合わせる例外を加えない。

### 4.6 HMDにおける同名Classのmodule選択

FSM及びBSMには、異なるmoduleに属する同じ`class_term`を候補として保持できる。ただし、
一つのHMDでは、同じ`class_term`について一つのmoduleのClassだけを選択する。

```text
HMD Class selection
= (selected_module, class_term)
```

同じHMDの同じ定義階層に、異なるmoduleの同名ClassをAssociationとして混在させては
ならない。どちらのmoduleを採用するかはprofile又は承認済み選択定義で明示し、入力順、
Association順、Class名、QName又は命名慣行から推測しない。Aligned ClassがShared Classを
特殊化する場合、SpecializationではShared super Classを参照できるが、HMDへは選択した
具体的な特殊化Classだけを出力する。

選択を一意にできない場合は当該HMDを正常成果物として生成せず、競合する
`(module, class_term)`及び到達経路を診断へ記録する。選択後のHMD部分集合では
`semantic_path`を一意とし、重複を命名処理で隠さない。

## 5. 行種別ごとの必須条件

| 行種別 | `module` | `class_term` | `associated_module` | `associated_class` | 処理 |
|---|---|---|---|---|---|
| Class／Abstract Class | 必須 | 必須 | 空欄 | 空欄 | Class identityを登録 |
| Attribute／Attribute(PK) | 必須 | 必須 | 空欄 | 空欄 | 参照先Classなし |
| Composition／Aggregation／Reference Association | 必須 | 必須 | 必須 | 必須 | Referenced Class identityを検証 |
| Specialization | 必須 | 必須 | 必須 | 必須 | childは`(module, class_term)`、superは`(associated_module, associated_class)` |
| LHM C | 必須 | 必須 | 所有Classのmodule | 列なし | Class行のmoduleを明示 |
| LHM 通常A | 必須 | 必須 | 所有Classのmodule | 列なし | 所有Class配下のAttribute |
| LHM R | 必須 | 必須 | 参照先module | 列なし | 参照先ClassはGraph Walk状態で保持 |
| LHM REF（`type=A`, `identifier=REF`） | 必須 | 必須 | 直前Rの参照先module | 列なし | 参照先PK由来。名前を再解析しない |

LHM及びそのHMD部分集合の`element`必須条件は次のとおりとする。

| 行種別 | `element` | 規則 |
|---|---|---|
| C | 必須 | Class conceptを生成する |
| A | 必須 | Attribute conceptを生成する |
| REF | 必須 | 直上Rが保持する参照先ClassのPKから生成する |
| R（multiplicity上限が1） | 空欄 | taxonomy conceptを生成しない |
| R（multiplicity上限が1を超える又は無制限） | 必須 | dimensionを生成する |

`0`及び`0..0`は削除指示でありLHMへ出力しない。R行の上限判定では、`1`、
`0..1`及び`1..1`を「上限1」とし、上限が2以上又は`*`を「上限1超」とする。
空欄又は解釈不能なmultiplicityは入力エラーとし、elementの要否を推測しない。

### 5.1 semantic_pathからelementを生成する規則

`element`を割り当てる意味概念は`semantic_path`で識別する。一つのLHM内で
`semantic_path`は一意でなければならない。同じ`semantic_path`が重複した場合は、
element名の補正ではなくHMDのmodule選択又は入力モデルのエラーとして扱う。

1. `semantic_path`の末尾segmentを最初の候補とし、prefixを含まない
   lowerCamelCaseのXML Schema NCNameへ変換する。
2. 同じmodule内の異なる`semantic_path`が同じ候補になる場合、末尾から直近の
   上位segmentを順次前置し、一意になる最短suffixを使用する。
3. 上位segmentの末尾語と下位segmentの先頭語が同じ場合、その語は一回だけ出力する。
4. 一意性はHMD単位ではなくmodule単位で判定する。異なるmoduleでは同じelementを
   使用できる。
5. 同じmodule及び同じ`semantic_path`が複数HMDに現れる場合は同じelementを使用する。
6. 入力順、`sequence`、自動連番又はhashによって衝突を解消しない。全segmentを
   使用しても一意にならない場合は命名エラーとし、承認済みelement mappingで解決する。
7. taxonomy prefix及びnamespace URIは後続のsyntax bindingで割り当てる。

REF行の`semantic_path`は、Graph WalkがR行生成時に保持したassociation role及び
参照先ClassのPK propertyから構成する。REF属性名、Class名、QName又はmodule名だけから
参照関係を推測しない。

Specializationは既存の`associated_class`をsuper class参照に使用しているため、
新しい参照列を増やさず、同じ`associated_module`と`associated_class`を使用する。
その他の行種別にClass参照が見つかった場合は、既存列の意味を確認してから本原則を
適用し、推測だけで列を追加しない。

Association行で`associated_module`又は`associated_class`が空欄の場合、又は
指定した組合せのClassが存在しない場合は入力モデルのエラーである。同一module内の
参照でも`associated_module`を必須とする。

次を禁止する。

- 空の`associated_module`へ所有Classの`module`を補完する。
- Class名、先頭文字、接頭辞、QName又は命名規則からmoduleを推測する。
- 同名Classの候補からID、sequence又は入力順で一件を選択する。
- QName prefix又はnamespace prefixをlogical moduleとして暗黙使用する。
- 後方互換性を理由に警告だけで曖昧なAssociationをBSMへ反映する。

PoCでは他のClassの処理を継続できるが、参照不能なAssociationは
`unreflected`又は`needs-review`として診断reportへ記録し、BSMへ反映しない。
ReferenceならR／REF、Compositionなら当該edgeからの展開を出力しない。QNameを含む
ClassはClassと依存行、QNameを含むSpecializationは当該特殊化を隔離し、独立した
ClassのPoC処理を継続する。

Specializationのsuper Classは
`(associated_module, associated_class)`で識別する。super Classが解決不能な場合、
Specializationを適用せず、当該child Class全体とそのpropertyを正常BSMへ出力しない。
child固有propertyは診断reportへ記録し、独立した他Classは処理を継続する。

## 6. Specialization／extension

super classとchild classのAssociation property identityがそれぞれ一意に一致する場合、
child側の`property_type`及び`multiplicity`で上書きする。`property_type`の変更は
別Associationの追加ではない。

child側の`multiplicity`が`0`又は`0..0`なら継承Associationを削除し、BSM、
LHM及びtaxonomyへ出力しない。一致するsuper propertyがない新規Associationで
`0`又は`0..0`を指定した場合も有効propertyとして出力しない。

同一Class内の重複Associationは入力エラーとして報告する。PoCではモデル全体を
停止せず、重複のないClass及び一意に処理できるpropertyを継続する。曖昧なpropertyを
ID、sequence、入力順、最初／最後、`property_type`又は`multiplicity`で選ばず、
暗黙統合、role推測、role書換え又は連番付与を行わない。

## 7. 診断及びPoC成果物

Association重複、未定義module又はClass参照の診断reportには少なくとも次を含める。

- 入力モデル及び入力ファイル
- 対象、super及びchild Classの`module`、`class_term`及びID
- `property_term`
- `associated_module`及び`associated_class`
- super及びchild側の該当property一覧
- 各行の`property_type`、`multiplicity`、行番号又は`sequence`
- property ID又はFSM ID
- error又はwarningの理由
- 実際に適用した処理
- BSMへの反映結果
- 未反映又は要確認となった内容

BSMの処理状態はsemantic core列へ追加せず、manifestを正本とし、詳細を診断report、
必要なproperty単位の状態をsidecarに記録する。

```text
processing_status = poc-with-errors
error_count       = n
warning_count     = n
report_file       = <diagnostic report>
```

入力読取り不能、構文解析不能、Class又はpropertyを識別できない必須列不足、出力不能、
既存ファイル破損のおそれは対象入力を生成不能とする致命的エラーである。

PoC実施作業者（三分一）は診断reportを確認して次工程への進行を判断する。header不一致、
Class identity不明、super参照不能childの隔離、未解決Association／Specialization又は
隔離行の正常行混在がある成果物をconsumerは正常成果物として受理しない。PoC継続用に
中間fileを手修正する場合は、元file、修正後file、箇所、理由、修正者・日時、対応error、
進行理由及び実行結果を記録し、正式自動生成結果と区別する。

## 8. 通常処理と既存データ移行

通常処理では空欄の`associated_module`を同じ行の`module`で補完しない。既存データの
移行に限り、承認された移行表又は専用変換スクリプトで明示的に設定できる。入力file
とSHA-256、行識別、所有Class、行種別、移行前後、理由、自動／手動、要確認及び確認
結果を記録し、人が承認したfileだけを正規入力とする。旧QNameも通常処理では分割せず、
この明示的移行手続を使う。

移行mapping及び`associated_module`を明示した改訂FSM表の作成者・確認者はPoC実施
作業者（三分一）とする。変更対象fileと行、Association／Specialization区分、
参照元・参照先identity、追加又は修正値、判断根拠及び確認日を記録する。

## 9. module台帳とsyntax binding

共通module–namespace対応台帳は
`bindings/taxonomy/module-namespace-bindings.csv`に置く。列は`module`,
`taxonomy_prefix`, `namespace_uri`, `taxonomy_version`, `namespace_date`,
`taxonomy_entry_point`, `status`とする。作成・更新及びPoC採用判断はPoC実施作業者
（三分一）、内容確認はtaxonomy担当reviewerが行う。個別syntax bindingは原則として
HMD単位で作成する。今回は台帳データを作成しない。

## 10. 適用版とcontract識別

新契約はtaxonomy version `2026-12-31`から適用する。

| モデル | contract name | contract version | 列数 |
|---|---|---|---:|
| FSM | `xbrl-gl-next-fsm` | `2026-12-31` | 14 |
| BSM | `xbrl-gl-next-bsm` | `2026-12-31` | 15 |
| LHM | `xbrl-gl-next-lhm` | `2026-12-31` | 17 |

旧・新契約はfile名だけで識別せず、manifestのcontract name、version、列順及び
SHA-256を必須とする。HMDはLHMと別形式ではなく、LHMからroot Class単位で識別又は
抽出した同一17列契約の階層定義とする。

## 11. producer／consumer影響

| 対象 | 現状 | 必要な改訂 |
|---|---|---|
| `tools/semantic/specialization.py` | Classを`class_term`だけで登録し、Associationを`(property_term, associated_class)`で照合。moduleを補完しQName形式へ修飾 | 14列FSMを必須検査し、Classを複合keyで登録。`element`なし15列BSMを出力。super参照不能child全体を隔離 |
| `tools/semantic/graphwalk.py` | 15列BSMを入力し、Class名／QName表記を中心に参照。19列LHMを出力 | 新15列BSMを入力し、複合Class keyで探索。17列LHMを出力 |
| `tools/semantic/bie_to_fsm.py` | CCL確認用でpipeline外 | 使用再開時に14列FSM契約を適用 |
| `tools/taxonomy/xBRLGL_TaxonomyGenerator.py` | 旧19列LHM、`abbreviation_path`、`xpath`及び文字列からのmodule抽出へ依存 | 17列HMDを`(module, class_term)`単位で読み、QName／namespace割当をbinding内で実行 |
| `tests/test_specialization.py` | 既存header及び旧identityをfixture化 | 14／15列、複合Class key、必須`associated_module`、child隔離、重複及びPoC継続を追加 |
| `tests/test_graphwalk.py` | 15列BSMと旧19列LHMをfixture化 | 新15列BSMと17列LHMへ改訂 |
| 既存FSM／BSM／LHM CSV | `associated_module`なし | 別工程で明示的なmigration mappingを作成。今回は変更しない |
| downstream consumer | 旧列順又はQName表記へ依存する可能性 | header名で読み、manifestのcontract versionを検査 |

## 12. 実装前受入試験

| 試験条件 | 期待結果 |
|---|---|
| 同じrole＋同じassociated_module＋同じassociated_class | 重複を報告 |
| 同じrole＋異なるassociated_module＋同じassociated_class | 別Association |
| 異なるrole＋同じ参照先Class | 別Association |
| 同一module内参照でassociated_moduleを明記 | 正常 |
| 同一module内参照でassociated_moduleが空欄 | 入力エラー |
| 異なるmoduleへの参照 | 指定されたmoduleとClassの組合せで解決 |
| associated_moduleが未定義 | 入力エラー |
| associated_classが指定module内に存在しない | 入力エラー |
| 同名Classが複数moduleに存在 | FSM／BSMでは候補を区別して保持し、HMDでは明示された一つのmoduleだけを選択 |
| 一つのHMDで異なるmoduleの同名Classを混在 | 選択エラー。競合Classと到達経路を報告し、正常HMDを生成しない |
| property_typeだけが異なる | 同一Association候補として重複を報告 |
| multiplicityだけが異なる | 同一Association候補として重複を報告 |
| superとchildの識別keyが一致 | child側の特性で上書き |
| childのproperty_typeが異なる | child側の値で上書き |
| childのmultiplicityが異なる | child側の値で上書き |
| childのmultiplicityが0又は0..0 | 継承Associationを削除 |
| 一致superなしの新規Associationが0又は0..0 | 有効propertyとして出力しない |
| 前後又は内部に連続空白があるセル | `whiteSpace="collapse"`適用後の値で処理 |
| tab、改行又は復帰を含むセル | 空白置換及びcollapse後の値で処理 |
| 大文字・小文字だけが異なる | 異なる値として扱う |
| QName prefixだけからmoduleを推測できそうな入力 | 推測せず、明示されたmoduleだけを使用 |
| 一部Associationの参照先を解決できない | 当該Associationを未反映として報告し、他のPoC処理を継続 |
| 一部ClassにAssociation重複がある | 曖昧propertyを未反映とし、他のClassを処理してBSMを生成 |
| 入力ファイルを解析できない | 対象ファイルを生成不能として停止 |
| BSM headerが15列契約と異なる又は`element`を含む | consumerは入力契約エラーを報告 |
| LHM headerが17列契約と異なる又は`path`を含む | Graph Walk consumerは入力契約エラーを報告 |
| semantic_pathがLHM又は選択HMD内で重複 | module選択又は入力モデルのエラー。elementの連番等で隠さない |
| C、A又はREFのelementが空欄 | 出力契約エラー |
| Rのmultiplicity上限が1でelementがある | 出力契約エラー |
| Rのmultiplicity上限が1を超えるのにelementが空欄 | dimension生成に必要なelement欠落としてエラー |

追加のQName、module正規化、移行、R／REF及びend-to-end試験を含む番号付き試験表は
`TaxonomyFramework/REGRESSION_31_INTEGRATION_CONDITIONS.md`第5.1節を正本とする。
件数は仕様から数え、過去の4件、28件又は31件へ合わせない。

## 13. extension／sidecarとmanifest

canonical `id`はBSM／LHMのClass又はpropertyを版を越えて参照する安定識別子とし、
core内で必須かつ一意とする。物理入力順だけからIDを生成しない。

WORK固有の`fsmid`、`inherited`、`UNID`、`TDED`、`context`及び`short_name`は、
provenance、inheritance trace、external reference、semantic context及び
label／presentationの責務別sidecarへ保持する。sidecarはcanonical `id`でcoreへjoinする。

manifestのcore情報にはcontract version、path、columns及びSHA-256を含める。

```json
{
  "schemaVersion": "1.1",
  "modelId": "xbrl-gl-next",
  "modelVersion": "2026-12-31",
  "core": {
    "path": "bsm.csv",
    "contract": "xbrl-gl-next-bsm",
    "contractVersion": "2026-12-31",
    "columns": 15,
    "sha256": "..."
  },
  "processing": {
    "processing_status": "poc-with-errors",
    "error_count": 2,
    "warning_count": 1,
    "report_file": "reports/specialization-diagnostics.json"
  }
}
```

## 14. エンドツーエンド受入及び正式化条件

1. ADR-0006及び本列契約を利用者が承認する。
2. 既存FSMの全Association及びSpecializationについて`associated_module`のmigration
   mappingを作成し、推測値を含めずreviewする。
3. `specialization.py`、`graphwalk.py`、taxonomy generator、binding、validation、
   fixture、期待結果、診断及びmanifest検証を一体の実装工程で管理する。commitは
   安全に検証できる目的別に分割できる。
4. Class identity、Referenced Class identity、Association property identity及び
   空白collapseをunit testで固定する。
5. Reference AssociationのR／REF停止、datatype、semantic path及びelementを検証する。
6. 同じ承認済み入力を2回処理し、core、sidecar及びmanifestのSHA-256一致を確認する。
7. BSMの`element`、LHMの`path`、`associated_class`、
   `abbreviation_path`、`xpath`、DNM及び`-o`が正式出力・CLI・試験に残らない。
8. `FSM → Specialization → BSM → Graph Walk → LHM → HMD選択／binding → taxonomy →
   instance/sample → Arelle等の検証`を最終受入単位とし、段階試験の合格だけを
   最終受入完了としない。
