# Open issues

Phase 0で論点の所在、影響、処置及び実施phaseを確定しました。未解決であることを
理由に出典又は公開区分を曖昧にせず、該当成果物は公開保留とします。

| ID | Priority | 論点 | 現在の判断 | 次の処置 | Phase |
| --- | --- | --- | --- | --- | --- |
| P0-01 | Blocker | GitHub remote、owner、visibility及びpublication authority | targetにはremoteがない。pushしない | repository ownerがremoteとprivate/publicを明示し、公開候補一覧を承認する | Publication gate |
| P0-02 | Blocker | XBRL由来prototypeが`xbrl.org` namespaceを使用 | 技術検証には保持するが、公式taxonomyとして公開できない | 公式taxonomyをimportする構成又はproject-owned namespaceへ移行し、attributionを保持する | Phase 1–3 |
| P0-03 | Blocker | XBRL GL licenseはtaxonomy本体の改変を制限 | 現在のTuple/OIM treeは公開保留 | XBRL International termsに適合するextension／reimplementation境界をlegal reviewする | Publication gate |
| P0-04 | Blocker | UN/CEFACT D25A派生CSVの再配布権限 | free-of-charge useと再配布・派生物公開を同一視しない | official download recipeへ置換するか、書面許可を取得する | Publication gate |
| P0-05 | High | CCL D25A元fileのURLとchecksumを復元できない | release identifierのみ確認済み | row unique ID、official package、取得日及びchecksumをprovenance tableへ追加する | Phase 3 |
| P0-06 | High | Tuple experimentにlocal missing dependencyが5件ある | 正式entry pointから除外 | self-contained fixture又はprofile resolverへ再構成する | Phase 1 |
| P0-07 | High | `FSM_btx`のmodule空欄640件 | `(module, class_term)`を作れないためcanonical FSMへ移行不能 | 出典に基づく明示mapping又はsource訂正をreviewし、確定不能行は除外reportへ記録する。命名規則から推測しない | Phase 3 |
| P0-08 | High | generatorがvalid baselineを決定的に再生成できない | baselineは手編集済み完成例 | ADR-0003のassemblyをgenerator受入testにする | Phase 1–5 |
| P0-09 | High | Tuple 2015／2017 concept差分が未作成 | 公式packageとchecksumは確定 | concept、type、tuple path、role及びlinkbase差分を生成する | Phase 2 |
| P0-10 | Medium | `tools/semantic/bie_to_fsm.py`に明示licenseがない | private working限定 | author、copyright及びlicenseを記録する | Phase 1 |
| P0-11 | Medium | Framework DOCXの公開権限 | user-supplied開始点 | repository ownerが著作者・公開権限を承認する | Publication gate |
| P0-12 | Medium | DOCX/XLSX binary metadata検査 | text secret scanはpass | author property、hidden sheet、comment、embedded objectをrelease前に検査する | Phase 7 |
| P0-13 | Medium | OIM exampleのend-to-end検証 | taxonomy rootのみvalidity確認済み | vendor invoice metadata、CSV、facts及びround tripを検証する | Phase 5–6 |
| P0-14 | Medium | Shared／Aligned heuristic | governance approvalではない | provenanceと適用範囲に基づくreview registryを作成する | Phase 3／7 |
| P0-15 | Resolved | LHM/HMD用語 | LHMは全体、HMDはroot Class単位の識別・抽出。共通17列契約と`(module, class_term)` identityを使用 | 実装及びfixtureへ反映する | Phase 1 |
| P0-16 | Medium | consumer migration | baseline checksumのみ固定 | crosswalk、shadow generation及びrollback gateを実施する | Phase 6 |
| P0-18 | Blocker | WORK specialization 18列出力とgraphwalk旧15列入力の不整合 | FSM 14列、BSM 15列、LHM/HMD 17列をPoC実装基準とした。現行実装は未対応 | 基準仕様、program、fixture、期待結果及び試験を対応する一式としてPrivate GitHub登録候補化し、承認後に専用branchで改訂する | Phase 1 |
| P0-19 | High | DNM `-o`の残存実装 | DNMは非サポートと決定 | option、分岐、出力、help、例及びDNM専用testを後続実装で削除 | Phase 1 |
| P0-20 | High | WORK版18列の追加項目 | 5種の責務別sidecarとmanifest案を定義 | 既存FSMでID衝突、欠落、join多重度及びconsumer影響を試験 | Phase 1 |
| P0-21 | High | Association同一keyの重複 | 重複入力エラーとして報告するが、PoCではモデル全体を停止しない | super／child対比、曖昧property未反映、他Class継続及び診断項目を実装・試験 | Phase 1 |
| P0-22 | High | semantic toolの版統合 | WORK、4件及び28件に独立機能が分散 | 一版の上書きを禁止し、機能単位統合案を承認する | Phase 1 |
| P0-23 | Medium | `xBRL-GL2.0_btx`と`taxonomy/oim/prototype`の重複 | taxonomy 46件が相対path・SHAとも全件一致 | DTS、sample、tool、生成物及びprovenanceへ分離する配置案を承認する | Phase 1 |
| P0-24 | High | semantic_pathからのelement生成 | semantic_pathを意味識別子とし、module内で一意な最短suffix由来のlowerCamelCase NCNameを生成。C／A／REF必須、Rはmultiplicity上限で要否を判定。実装未改訂 | AT-074～AT-094をfixture化し、Graph Walkの再現性まで検証する。taxonomy generator／consumer実装は後続 | Phase 1 |
| P0-25 | High | エラーを含むPoC BSMの状態管理 | 15列coreへ処理状態を追加せずmanifestを状態の正本とする | `processing_status`、件数、report path／hash、property状態sidecar及びconsumer拒否条件をschema化 | Phase 1 |
| P0-26 | Blocker | `associated_module`を持たない既存FSM／BSM／LHMの移行 | Class identityを`(module, class_term)`、参照先を`(associated_module, associated_class)`とするADR-0006案を作成 | 既存全参照の明示mapping、review、移行時診断及びrollbackを承認する。推測補完は禁止 | Phase 1 |
| P0-27 | Resolved | Specializationのsuper Class参照不能時の隔離単位 | child全体を正常BSMから隔離し、child固有propertyを診断reportへ記録 | 実装及び試験へ反映する | Phase 1 |
| P0-28 | Resolved | module台帳とsyntax binding対応表 | `bindings/taxonomy/module-namespace-bindings.csv`の7列案と管理責任を確定 | 現行taxonomyでentry point列の必要性を実装前確認 | Phase 1 |
| P0-29 | High | 旧・新LHM/HMD契約の識別 | taxonomy version 2026-12-31から17列契約とmanifestのcontract name／versionを必須化 | schemaとconsumer拒否条件を実装前に承認する | Phase 1 |
| P0-30 | Resolved | 既存FSM移行の作成者・確認者 | PoC実施作業者（三分一）が作成・確認し、監査可能な明示mappingを保持 | 移行時に記録項目を検証する | Phase 1 |
| P0-31 | High | QName形式の意味モデル値 | 自動分割・module推測・警告受理を禁止し、影響scopeを隔離する | 診断schemaと旧QName移行mappingの承認手順を確定する | Phase 1 |
| P0-32 | High | 一つのHMDにおける異なるmoduleの同名Class混在 | FSM／BSMには候補を保持できるが、HMDは`(selected_module, class_term)`で一moduleだけを明示選択。混在は選択エラー | profile実装へ進む前に、最小fixtureで選択、競合、Aligned特殊化及びsemantic_path一意性を検証する | Phase 1 |

## Phase 0で解決した事項

- 2015公式packageをRecommendation `2015-03-25`として特定した。
- 2017 work productをPWD `2016-12-01`として特定した。
- 公式ZIPのURL、size、file count及びSHA-256を固定した。
- UADAから選択コピーした99ファイルがコピー時点ですべて同一であることを確認した。
  現在は97件同一、WORK側で意図的に改訂した2件をdifferentとして追跡している。
- UADA側とWORK側のGit rootを区別した。
- DTS dependency 478 edgeとlocal missing 5件を特定した。
- consumer LHM baseline 8件のchecksumを固定した。
- GitHub登録候補、private限定、公開保留及び対象外を区分した。
- high-confidence secret scanで検出0件を確認した。
- full `tools` compileで既存prototypeの構文エラー1件を検出し、P0-17へ登録した。
- P0-17の`specialization.py`をWORK側で改訂し、property同一性、変更、追加、
  multiplicity `0`による削除、循環検出及びCLIをunit testで固定した。
