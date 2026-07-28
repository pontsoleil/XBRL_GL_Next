[English](OPEN_ISSUES.md) | **日本語**

# 未解決課題

Phase 0で論点の所在、影響、処置及び実施phaseを確定しました。未解決であることを
理由に出典又は公開区分を曖昧にせず、該当成果物は登録又は公開保留とします。

| ID | Priority | 論点 | 現在の判断 | 次の処置 | Phase |
| --- | --- | --- | --- | --- | --- |
| P0-01 | Blocker | GitHub owner、visibility、publication authority及びpush承認 | targetには現在`origin` remoteと専用branchがあるが、それ自体は公開又は各pushの許可ではない | repository ownerがvisibilityとpublication authorityを確認し、登録単位ごとに承認する | Publication gate |
| P0-02 | Blocker | XBRL由来prototypeが`xbrl.org` namespaceを使用 | 技術検証には保持するが、公式taxonomyとして公開できない | 公式taxonomyをimportするか、独立管理conceptをproject-owned namespaceへ移行しattributionを保持する | Phase 1–3 |
| P0-03 | Blocker | XBRL GL licenseはtaxonomy内容の改変を制限 | 現在のTuple/OIM treeは公開保留 | XBRL International条件に適合するextension／reimplementation境界をlegal reviewする | Publication gate |
| P0-04 | Blocker | UN/CEFACT D25A派生CSVの再配布権限 | free-of-charge useと再配布・派生物公開を同一視しない | official download recipeへ置換するか書面許可を取得する | Publication gate |
| P0-05 | High | CCL D25A元fileのURLとchecksumを復元できない | release identifierのみ確認済み | row unique ID、official package、取得日及びchecksumをprovenance tableへ追加する | Phase 3 |
| P0-06 | High | Tuple experimentにlocal missing dependencyが5件ある | 正式entry pointから除外 | self-contained fixture又はprofile resolverへ再構成する | Phase 1 |
| P0-07 | High | `FSM_btx`のmodule空欄640件 | `(module, class_term)`を作れずcanonical FSMへ移行不能 | 出典に基づく明示mapping又はsource訂正をreviewし、確定不能行は除外reportへ記録する。命名規則から推測しない | Phase 3 |
| P0-08 | High | generatorがvalid baselineを決定的に再生成できない | baselineは手編集済み完成例 | 再評価後、ADR-0003のassemblyをgenerator受入testにする | Phase 1–5 |
| P0-09 | High | Tuple 2015／2017 concept差分が未作成 | 公式packageとchecksumは確定 | concept、type、tuple path、role及びlinkbase差分を生成する | Phase 2 |
| P0-10 | Medium | `tools/semantic/bie_to_fsm.py`に明示licenseがない | Private WORK分析限定 | author、copyright及びlicenseを記録する | Phase 1 |
| P0-11 | Medium | Framework DOCXの公開権限 | user-supplied開始点 | repository ownerが著作者・公開権限を承認する | Publication gate |
| P0-12 | Medium | DOCX/XLSX binary metadata検査 | text secret scanはpass | author property、hidden sheet、comment、embedded objectをrelease前に検査する | Phase 7 |
| P0-13 | Medium | OIM exampleのend-to-end検証 | taxonomy rootのみvalidity確認済み | vendor invoice metadata、CSV、facts及びround tripを検証する | Phase 5–6 |
| P0-14 | Medium | Shared／Aligned heuristic | governance approvalではない | provenanceと適用範囲に基づくreview registryを作成する | Phase 3／7 |
| P0-15 | In progress | LHMとHMDの用語 | Graph Walkは17列LHMを生成。HMDはbinding段階で選択するメッセージ単位の部分集合。単一root LHMは対応HMDと内容上同一 | 残る文書とHMD／binding実体を継続確認する | Phase 1 |
| P0-16 | Medium | consumer migration | baseline checksumのみ固定 | crosswalk、shadow generation及びrollback gateを実施する | Phase 6 |
| P0-18 | High | Semantic pipeline統合 | FSM 14列、BSM 15列、LHM 17列を実装・試験済み。HMD／bindingはGraph Walk外で継続確認 | Semantic一式を承認後に登録し、HMD／bindingを別工程で検証する | Phase 1 |
| P0-19 | High | DNM `-o`の残存実装 | DNMは非サポート | option、分岐、出力、help、例及びDNM専用testを後続実装で削除する | Phase 1 |
| P0-20 | High | WORK版18列の追加項目 | 5種の責務別sidecarとmanifest案を定義 | 既存FSMでID衝突、欠落、join多重度及びconsumer影響を試験する | Phase 1 |
| P0-21 | High | Association同一keyの重複 | 重複入力エラーとして報告するがPoCではmodel全体を停止しない | super／child対比、曖昧property未反映、他Class継続及び診断項目を実装・試験する | Phase 1 |
| P0-22 | High | semantic tool世代統合 | WORK、4件及び28件に独立機能が分散 | 一版の上書きを禁止し機能単位統合案を承認する | Phase 1 |
| P0-23 | Medium | `xBRL-GL2.0_btx`と`taxonomy/oim/prototype`の重複 | taxonomy 46件が相対path・SHAとも全件一致 | DTS、sample、tool、生成物及びprovenanceへ分離する配置案を承認する | Phase 1 |
| P0-24 | High | `semantic_path`からの`element`生成 | `semantic_path`を意味識別子としmodule内で一意な最短suffix由来lowerCamelCase NCNameを生成。C／A／REF必須、Rはmultiplicity上限で要否判定。program未改訂 | AT-074～AT-094をfixture化しGraph Walk再現性まで検証する。generator／consumerは後続 | Phase 1 |
| P0-25 | High | エラーを含むPoC BSMの状態管理 | 15列coreへ状態を追加せずmanifestを正本とする | processing status、件数、report path／hash、property status sidecar及びconsumer拒否条件をschema化する | Phase 1 |
| P0-26 | Blocker | `associated_module`を持たない既存modelの移行 | ADR-0006がClass及び参照先Class identityを定義 | 既存全参照の明示mapping、review、移行診断及びrollbackを承認する。推測は禁止 | Phase 1 |
| P0-27 | Resolved | Specializationのsuper Class参照不能時の隔離単位 | childを正常BSMから隔離しchild固有propertyをdiagnostic reportへ記録 | 実装及び試験へ反映する | Phase 1 |
| P0-28 | Resolved | module台帳とsyntax binding対応表 | 7列binding表と管理責任を定義し、`taxonomy_entry_point`はrelease manifestで管理 | 正式保存場所を確認し、manifest／binding validationを後続実装する | Phase 1 |
| P0-29 | High | 旧・新LHM契約の識別 | taxonomy version `2026-12-31`から17列LHM契約とmanifest contract name／versionを必須化 | schemaとconsumer拒否条件をbinding実装前に承認する | Phase 1 |
| P0-30 | Resolved | 既存FSM移行mappingの作成者・確認者 | PoC実施作業者が作成・確認し監査可能な明示mappingを保持 | 移行時に必須記録を検証する | Phase 1 |
| P0-31 | High | QName形式の意味モデル値 | 自動分割、module推測及びwarning受理を禁止 | diagnostic schemaと旧QName移行mappingの承認手順を確定する | Phase 1 |
| P0-32 | High | 一つのHMDにおける異なるmoduleの同名Class混在 | FSM／BSMには候補を保持できるがHMDは一つの`(selected_module, class_term)`だけを選択し混在禁止 | profile実装前に選択、競合、Aligned特殊化及び`semantic_path`一意性を試験する | Phase 1 |
| P0-33 | High | `LICENSE.md`が生成artifact全般へCC BY 4.0を適用するように読める | owner承認なしに既存license fileを変更しない。README／noticeの限定説明は識別済みproject-authored資料だけに適用 | file単位のlicense判断後、外部原本、派生成果物及びconsumer dataを再ライセンスしない形で`LICENSE.md`を整合させる | Publication gate |

## Phase 0で解決した事項

- 2015公式packageをRecommendation `2015-03-25`として特定した。
- 2017 work productをPWD `2016-12-01`として特定した。
- 公式ZIPのURL、size、file count及びSHA-256を固定した。
- UADAから選択コピーした99fileがcopy時点ですべて同一であることを確認し、現在は
  97件同一、WORK側で意図的に改訂した2件をdifferentとして追跡している。
- UADA側とWORK側のGit rootを区別した。
- DTS dependency 478 edgeとlocal missing 5件を特定した。
- consumer LHM baseline 8件のchecksumを固定した。
- GitHub登録候補、Private限定、公開保留及び対象外を区分した。
- high-confidence secret scanで検出0件を確認した。
- full `tools` compileで既存prototypeの構文error 1件を検出しP0-17へ登録した。
- P0-17のWORK `specialization.py`を改訂し、property identity、変更、追加、
  multiplicity `0`による削除、循環検出及びCLIをunit testで固定した。
