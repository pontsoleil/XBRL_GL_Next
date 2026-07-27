# semantic tool機能単位統合条件

> ファイル名は過去資料との対応のため今回変更しない。31件版を正式採用する文書ではない。

## 1. 名称変更案

正式GIT登録時の候補名:

```text
docs/testing/semantic-functional-integration-conditions.md
```

名称変更時に更新する参照元:

- `TaxonomyFramework/PHASE1_PREBRANCH_PLAN.md`
- `TaxonomyFramework/REUSE_DECISIONS.md`（世代説明）
- `TaxonomyFramework/MIGRATION_PLAN.md`
- `docs/Codex/20260726_0903/**`（履歴資料のため内容は改変せず、移行対応表だけで参照）

今回はファイル名及び配置を変更しない。

## 2. 統合対象

| 区分 | 所在 | 対応試験 | 現在の位置付け |
|---|---|---:|---|
| WORK版 | `tools/semantic/` | native 6件合格 | 追加列及び`bie_to_fsm.py`の比較元。DNM `-o`は削除対象 |
| 単独4件版 | `docs/ChatGPT/20260725_145244/programs/` | 4件合格 | 要素名生成及び空association role等の部分比較 |
| 28件版 | `docs/ChatGPT/20260725_153459/programs/` | 28件合格 | formal header、Abstract、旧QName処理、Reference及びdatatypeの比較資料 |

いずれか一版をそのまま正式採用せず、機能単位で統合する。状況報告上の31件版は
過去記録であり、探索、回収、正式採用又は31件という件数の再現を作業条件にしない。

## 3. 機能単位の採用条件

| 機能 | 統合条件 |
|---|---|
| FSM header alias | 値を変更せずheaderだけcanonical nameへ正規化。改訂契約は14列 |
| BSM | FSM 14列＋末尾`id`の15列canonical semantic core。`element`なし |
| LHM/HMD | 共通17列。`semantic_path`、`associated_module`、HMD identity用`class_term`を保持し、`path`、`associated_class`、`abbreviation_path`、`xpath`を除く |
| Association | keyは`(property_term, associated_module, associated_class)`。空roleを保持し、同一key重複を報告してPoC処理を継続 |
| Abstract Class | 通常Classからの参照を報告・除外し、Abstract Class自体をBSMへ出力しない |
| module／logical class | Classは`(module, class_term)`、参照先は`(associated_module, associated_class)`で検査。QNameはsyntax bindingだけで扱う |
| Reference | R／REFを出力して探索停止し、datatypeを保持 |
| 複数root | root順序、重複及び再現性を試験 |
| element | semantic path後にprefixなしlowerCamelCase NCNameを生成。module内で一意となる最短suffixを使い、重複語を除き、連番・入力順・hashを禁止 |
| HMD Class選択 | FSM／BSMの異なるmoduleにある同名Classは候補として保持できるが、一つのHMDでは一つのmoduleだけを明示選択し、混在を禁止 |
| WORK追加項目 | 15列へ追加せず、責務別sidecar及びmanifestで保持 |
| DNM | 非サポート。`-o`、分岐、出力、例、help及びDNM専用testを後続実装で削除 |
| `bie_to_fsm.py` | CCLチェック用途を確認するまで正式pipeline外 |

## 4. 統合前の共通合格条件

- formal FSM headerを実際の列名で読み取る。
- multiplicity `0`又は`0..0`を削除指示とし、有効propertyとして出力しない。
- Association重複をsuper／child各Classでextension前に検出するが、入力モデル全体は
  停止しない。曖昧propertyを暗黙に選択又は統合せず、未反映／要確認として報告し、
  重複のないClass及び一意なpropertyをBSMへ出力する。
- roleをassociated class、Class名、LC3又は業務文脈から推測・生成しない。
- 通常ClassからAbstract ClassへのAssociationを検出・報告・除外する。
- module、class term、associated module及びassociated classによる論理参照を検査する。
- Class名先頭文字によるmodule推測が存在しない。
- datatypeを保持する。
- Reference AssociationでR／REFを出力して探索を停止する。
- 未定義module、未定義associated module、未定義associated class及び論理Class参照の曖昧性を入力エラーとする。
- `Accountant_ Contact_ Phone`から`Acc:Phone`を生成しない。
- 14列FSM、15列BSM及び17列LHM/HMDのheaderと順序が契約に一致する。
- BSMの`element`、LHM/HMDの`path`、`associated_class`、`abbreviation_path`、
  `xpath`、DNM及び`-o`が正式出力・CLI・testに存在しない。
- 3版から移植した各試験について、由来、fixture、期待値及び列契約を記録する。
- BSM manifestへ`processing_status`、error／warning件数及び診断reportを記録し、
  `poc-with-errors`をcleanな正式成果物として扱わない。

新しい正式試験件数は、採用機能とGitHub実データ試験を統合した後に数え直す。
4件、28件又は31件という過去の件数自体を合否条件にしない。

## 5. element試験

少なくとも次を固定fixtureにする。

| semantic構成 | 期待element |
|---|---|
| `Identifier` | `identifier` |
| `Party / Identifier` | `partyIdentifier` |
| `Seller / Party / Identifier` | `sellerPartyIdentifier` |
| `Invoice Line / Line Identifier` | `invoiceLineIdentifier` |

末尾segmentから開始し、同じmodule内で一意になるまで直近の上位segmentを前置する。
隣接segment境界で同じ語が重なる場合は一回だけ出力する。全segmentを使っても一意に
ならないfixtureでは、連番、入力順及びhashを使わず命名エラーを期待する。

## 5.1 実装前受入試験仕様

| ID | 入力条件 | 期待結果 | 工程 | 最終受入との関係 |
|---|---|---|---|---|
| AT-001 | 同じrole・associated module・class | 重複を報告し曖昧propertyを未反映 | Specialization | 前提 |
| AT-002 | 空roleで同じ参照先 | 重複を報告しPoC継続 | Specialization | 前提 |
| AT-003 | 同じrole・異なるassociated module・同じclass | 別Association | Specialization | 前提 |
| AT-004 | 異なるrole・同じ参照先 | 別Association | Specialization | 前提 |
| AT-005 | property_typeだけ異なる同一key | 重複 | Specialization | 前提 |
| AT-006 | multiplicityだけ異なる同一key | 重複 | Specialization | 前提 |
| AT-007 | super／childのkey一致 | child特性で上書き | Specialization | 前提 |
| AT-008 | childのproperty_type変更 | 同一propertyとして上書き | Specialization | 前提 |
| AT-009 | childのmultiplicity変更 | 同一propertyとして上書き | Specialization | 前提 |
| AT-010 | child multiplicity `0`／`0..0` | 継承propertyを削除 | Specialization | 前提 |
| AT-011 | 一致superなしの新規propertyが`0`／`0..0` | 有効propertyとして出力しない | Specialization | 前提 |
| AT-012 | 一部Classだけ重複 | 他Classを処理し、部分BSMと診断を生成 | Specialization | 部分成果物 |
| AT-013 | 同一module内でassociated_module明記 | 正常 | Specialization | 前提 |
| AT-014 | 通常処理でassociated_module空欄 | 補完せず入力エラー、当該参照を未反映 | Specialization | 部分成果物 |
| AT-015 | 異なるmodule参照 | 明示した組合せで一意に解決 | Specialization | 前提 |
| AT-016 | associated_module未定義 | 入力エラー、当該参照を未反映 | Specialization | 部分成果物 |
| AT-017 | 指定module内にClassなし | 入力エラー、当該参照を未反映 | Specialization | 部分成果物 |
| AT-018 | 同名Classが複数module | FSM／BSMではmodule-qualified候補として区別して保持 | Specialization | 前提 |
| AT-019 | super Class参照不能 | child全体を正常BSMから隔離し、独自propertyを診断へ記録 | Specialization | 前提 |
| AT-020 | 管理文字列の前後・連続空白 | token相当collapse | 全工程 | 前提 |
| AT-021 | module／associated_moduleのASCII大文字 | collapse後に小文字化 | 全工程 | 前提 |
| AT-022 | 小文字化後のmodule衝突 | 入力エラー | validation | 前提 |
| AT-023 | Class名／property termの大小文字差 | 異なる値 | 全工程 | 前提 |
| AT-024 | definition内の連続空白 | 原文を保持 | CSV I/O | 前提 |
| AT-025 | definition内の改行 | 引用fieldで保持 | CSV I/O | 前提 |
| AT-026 | class_termがQName形式 | 入力エラー。Classと依存行を隔離 | validation | 部分成果物 |
| AT-027 | associated_classがQName形式 | 入力エラー。当該Associationを隔離 | validation | 部分成果物 |
| AT-028 | property_termがQName形式 | 入力エラー。当該propertyを隔離 | validation | 部分成果物 |
| AT-029 | QNameを分割できそうな入力 | 自動分割、local name採用をしない | validation | 前提 |
| AT-030 | QName prefixからmoduleを推測できそうな入力 | 推測しない | validation | 前提 |
| AT-031 | QNameを含むReference Association | R及びREFを出力しない | Graph Walk | 部分成果物 |
| AT-032 | QNameを含むSpecialization | 適用せず診断 | Specialization | 部分成果物 |
| AT-033 | 一部だけQName不正 | 独立Class／propertyを継続 | 全工程 | 部分成果物 |
| AT-034 | QNameエラー診断 | 入力file、行、列、値、scope、処置を記録 | diagnostics | 前提 |
| AT-035 | 旧QNameデータを通常処理 | 自動移行しない | migration | 前提 |
| AT-036 | 承認済みQName移行mapping | 変換前後、根拠、確認結果を記録 | migration | 移行gate |
| AT-037 | roleありReference | R name=`role + "_ " + class` | Graph Walk | 前提 |
| AT-038 | 空role Reference | R name=`associated_class` | Graph Walk | 前提 |
| AT-039 | R／REF name | QName prefixを含まない | Graph Walk | 前提 |
| AT-040 | LHM/HMD C行 | associated_module=所有module | Graph Walk | 前提 |
| AT-041 | LHM/HMD R行 | associated_module=参照先module。associated_class列なし | Graph Walk | 前提 |
| AT-042 | LHM/HMD REF行 | `type=A`, `identifier=REF`、associated_moduleは直前Rから継承 | Graph Walk | 前提 |
| AT-043 | REF行 | 参照先ClassのPKとdatatypeを保持 | Graph Walk | 前提 |
| AT-044 | REF名からtargetを推測できそうな入力 | nameを解析せずRの処理状態と階層を使用 | Graph Walk | 前提 |
| AT-045 | Reference配下 | REF以外の子孫を0件とする | Graph Walk | 前提 |
| AT-046 | explicit migrationで同じ行のmoduleを設定 | mappingと監査記録がある場合だけ許容 | migration | 移行gate |
| AT-047 | 未承認移行file | Next正規入力として拒否 | manifest | 移行gate |
| AT-048 | module台帳にないmodule | 入力エラー | validation | 前提 |
| AT-049 | syntax binding | 台帳からprefix／namespace URIを解決してQName生成 | taxonomy binding | 最終 |
| AT-050 | 旧19列LHM | 17列契約として誤認しない | manifest | 前提 |
| AT-051 | contract name／versionなし又は不一致 | 入力契約エラー | consumer | 前提 |
| AT-052 | Association参照不能 | 当該edgeだけ未反映、他を継続 | 全工程 | 部分成果物 |
| AT-053 | 入力を解析不能／必須識別列なし | 対象file生成不能として停止 | I/O | 致命的 |
| AT-054 | 段階unit testだけ合格 | 最終受入完了とはしない | governance | 最終gate |
| AT-055 | taxonomyと代表sample | Arelle等で妥当、module／namespace対応一致 | E2E | 最終 |
| AT-056 | 同一承認入力を2回処理 | BSM、LHM/HMD、taxonomy、manifestのSHA-256一致 | E2E | 最終 |
| AT-057 | 部分生成 | status、除外scope、error件数、reportをmanifestへ記録 | diagnostics | 最終gate |
| AT-058 | FSM header | 確定14列と完全一致 | contract | 前提 |
| AT-059 | BSM header | FSM 14列と同順＋15列目`id` | contract | 前提 |
| AT-060 | BSM | `element`列が存在せずSpecializationも生成しない | Specialization | 前提 |
| AT-061 | LHMとHMD | 同じ17列契約及び用語を使用 | contract | 前提 |
| AT-062 | LHM/HMD | `path`列なし、`semantic_path`あり | Graph Walk | 前提 |
| AT-063 | LHM/HMD | `element`及び`class_term`あり | Graph Walk | 前提 |
| AT-064 | 複数rootのLHM | `(module, class_term)`でHMDを識別・抽出 | Graph Walk | 前提 |
| AT-065 | 同名rootが複数module | moduleを含むHMD identityで区別 | Graph Walk | 前提 |
| AT-066 | HMD syntax binding | HMD単位で対応し、構文pathをLHM/HMDへ戻さない | binding | 最終 |
| AT-067 | 旧16列BSM／旧18・19列LHM | 暗黙読替えせず契約不一致又は明示移行 | migration | 移行gate |
| AT-068 | 変換不能Association | 入力行、identity、隔離範囲、後続影響をerror listへ記録 | diagnostics | 前提 |
| AT-069 | PoC手修正file | 元・修正版、箇所、理由、担当、日時、error、結果を記録し正式結果と区別 | governance | 最終gate |
| AT-070 | 一つのHMDで同じclass_termの候補が一moduleだけ | 明示選択されたClassで正常展開 | Graph Walk | 前提 |
| AT-071 | 一つのHMDで異なるmoduleの同名Classを混在 | 選択エラー。競合Classと到達経路を報告し正常HMDを生成しない | Graph Walk | 前提 |
| AT-072 | 異なるmoduleの異なるclass_termを一HMDで使用 | 正常。混在禁止の対象外 | Graph Walk | 前提 |
| AT-073 | Aligned Classが同名のShared Classを特殊化 | 選択した具体ClassだけをHMDへ出力 | 全工程 | 前提 |
| AT-074 | HMD内でsemantic_pathが重複 | module選択又は入力モデルのエラー。命名補正しない | Graph Walk | 前提 |
| AT-075 | semantic_path末尾segmentが一意 | 末尾segmentからlowerCamelCase NCNameを生成 | Graph Walk | 前提 |
| AT-076 | 同一moduleで末尾element候補が衝突 | 一意になる最短の上位segmentを前置 | Graph Walk | 前提 |
| AT-077 | 異なるmoduleでelement候補が同一 | 各moduleで同じelementを許容 | Graph Walk | 前提 |
| AT-078 | 同じmodule・semantic_pathが複数HMDに出現 | 同じelementを再現 | Graph Walk | 前提 |
| AT-079 | 上位末尾語と下位先頭語が同じ | 重複語を一回だけ出力 | Graph Walk | 前提 |
| AT-080 | element候補に空白、記号又は先頭不正文字 | prefixなしlowerCamelCase NCNameへ変換又は命名エラー | Graph Walk | 前提 |
| AT-081 | 入力行又はroot順を変更 | semantic_pathとelementが不変 | Graph Walk | 再現性 |
| AT-082 | 全segment使用後もelement衝突 | 連番、sequence及びhashを使わず命名エラー | Graph Walk | 前提 |
| AT-083 | 承認済みelement mappingがある衝突 | mappingの根拠を記録して指定elementを使用 | migration | 移行gate |
| AT-084 | C行のelementが空欄 | 出力契約エラー | Graph Walk | 前提 |
| AT-085 | A行のelementが空欄 | 出力契約エラー | Graph Walk | 前提 |
| AT-086 | REF行のelementが空欄 | 出力契約エラー | Graph Walk | 前提 |
| AT-087 | R行のmultiplicityが`1`、`0..1`又は`1..1` | element空欄、taxonomy conceptを生成しない | Graph Walk | 前提 |
| AT-088 | R行のmultiplicity上限が2以上又は`*` | dimension用elementを必須とする | Graph Walk | 前提 |
| AT-089 | R行のmultiplicity上限1でelementあり | 出力契約エラー | validation | 前提 |
| AT-090 | R行のmultiplicity上限1超でelementなし | dimension element欠落エラー | validation | 前提 |
| AT-091 | R行のmultiplicityが空欄又は解釈不能 | 要否を推測せず入力エラー | Graph Walk | 前提 |
| AT-092 | REFのsemantic_path生成 | Rが保持するrole及び参照先ClassのPKを使用 | Graph Walk | 前提 |
| AT-093 | REF名、Class名、QName又はmodule名だけで参照を推測可能 | 推測せずRの処理状態を使用 | Graph Walk | 前提 |
| AT-094 | 同一承認入力を2回処理 | semantic_path及びelementを含む17列LHM/HMDのSHA-256一致 | Graph Walk | 再現性 |

モデルエラー時はBSM、manifest及び診断reportを一組で検査する。入力読取り、構文解析、
必須識別列、出力書込み又は既存ファイル保護に関する致命的エラーだけは対象入力を
生成不能として停止できる。試験数94件は現時点の仕様案から数えたもので、過去の
4件、28件又は31件へ合わせたものではない。

## 6. 実データ再現性

正式入力候補はShared FSM 849行＋FSM_btx 180行とし、FSM_btx単独実行を合否に
使用しない。統合候補で次を2回実行する。

```text
FSM + FSM_btx
    ↓ specialization.py
15列BSM
    ↓ graphwalk.py
17列LHM/HMD
```

各回について、Association重複、未反映／要確認property、PoC処理状態、
Abstract Class参照、未定義associated module／class、
R／REF、Reference配下の非REF子孫、datatype空欄、semantic path重複、element重複、
sidecar join、診断report、終了コード及びSHA-256を記録する。

## 7. 実装開始gate

次を確認するまで、候補プログラムの統合、改変又は正式配置を行わない。

1. sidecar／manifest及び診断report schemaの実装形式、配置、終了コード及び
   `poc-with-errors`に対するconsumerの扱い。
2. canonical `id`生成規則を既存FSMへ適用したときの衝突件数。
3. 14列FSM、15列BSM及び17列LHM/HMDへ対応するproducer、taxonomy generator及びconsumer migration範囲。
4. 既存データへ`associated_module`を明示するreview済みmappingの作成方法。
5. 統合候補を作る別作業領域及び試験fixtureの配置。
