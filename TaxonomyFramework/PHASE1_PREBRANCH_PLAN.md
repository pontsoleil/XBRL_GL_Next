# 正式branch作成前の最終確認

## 1. 4資料の整合性

2026-07-25に次の4資料を再照合した。

- `TaxonomyFramework/REUSE_DECISIONS.md`
- `TaxonomyFramework/MIGRATION_PLAN.md`
- `TaxonomyFramework/LEGACY_TO_TARGET_MAPPING.csv`
- `TaxonomyFramework/inventory/reuse-asset-assessment.csv`

結果:

| 検査 | 結果 |
|---|---:|
| 評価台帳行数 | 370 |
| 旧新対応表行数 | 370 |
| 評価台帳のunique旧path | 370 |
| 旧新対応表のunique旧path | 370 |
| 一方にだけ存在するpath | 0 |
| SHA-256不一致 | 0 |
| 判定不一致 | 0 |
| 新配置候補不一致 | 0 |
| 必須項目空欄 | 0 |

判定件数は4資料で次の値に統一されている。

```text
reuse_as_is              1
adapt_and_reuse         31
reference_only          19
replace                  7
exclude                  0
needs_license_review   308
needs_design_decision    4
total                  370
```

WORK版、単独4件版及び28件版は、所在、SHA-256、列契約及び対応試験を分離して管理する。
いずれか一版を正式統合候補として上書き採用しない。状況報告上の31件版は一式未回収の
過去記録であり、探索、回収又は件数再現をPhase 1の条件にしない。
正式リポジトリは`main`、HEAD `4172d5f...`、`## main...origin/main`であり、
旧資産又はWORK成果物のコピーは行われていない。

## 2. 最初のcommit候補

次の表は、branch作成後も利用者の別指示を受けてから準備する。`include`は
現在のWORKファイルを無条件にコピーする意味ではなく、公開用path、相対参照及び
文言をレビューした版を対象とする。

| 現在のWORK path | 正式リポジトリ予定path | 処置 | 状態 | 採否 | 理由・前処理 |
|---|---|---|---|---|---|
| `.gitignore` | `.gitignore` | 改定 | `confirmed` | include | Python、validation、生成出力及びlocal workingの除外を最小化 |
| `README.md` | `README.md` | 改定 | `confirmed` | include | 全面改定の目的、縦長architecture、Phase、公開gate。未登録prototypeを現存扱いしない |
| `AGENTS.md` | `AGENTS.md` | 新規 | `confirmed` | include条件付き | ローカル絶対pathを除き、repository内作業規則だけにする |
| `THIRD_PARTY_NOTICES.md` | `NOTICE.md` | 改定 | `confirmed` | include | XBRL公式条件、外部取得方針及び公開保留を明記 |
| `docs/architecture.md` | `docs/architecture/overview.md` | 改定 | `confirmed` | include | Shared/Aligned/Distinctを最新定義へ修正し、FSM→BSM→LHM責務を確定 |
| `TaxonomyFramework/SEMANTIC_MODEL_COLUMN_CONTRACTS.md` | `docs/architecture/semantic-model-column-contracts.md` | 改定 | `provisional` | include条件付き | 2026-12-31適用のFSM 14列、BSM 15列、LHM/HMD 17列、QName入力禁止、R／REF、PoC継続、診断及びmanifest。利用者承認が必要 |
| `docs/decisions/0006-module-qualified-class-identity.md` | 同左 | 新規 | `provisional` | include条件付き | `associated_module`導入とsyntax binding分離の設計判断。利用者承認後にAcceptedへ変更 |
| `docs/decisions/0001-semantic-first-dual-binding.md` | 同左 | 改定 | `confirmed` | include | semantic-first及びdual bindingの設計判断 |
| `docs/decisions/0002-provider-consumer-release-contract.md` | 同左 | 改定 | `confirmed` | include | consumer切替境界とmanifest |
| `docs/work-plan.md` | `docs/migration/work-plan.md` | 改定 | `confirmed` | include | commit単位の段階計画へ更新 |
| `docs/workspace-integration.md` | `docs/migration/workspace-integration.md` | 改定 | `confirmed` | include条件付き | 個人環境の絶対pathをrepository相対又は役割名へ置換 |
| `TaxonomyFramework/REUSE_DECISIONS.md` | `docs/migration/reuse-decisions.md` | 改定 | `confirmed` | include | 370件の採否と3版の機能単位統合方針を保持 |
| `TaxonomyFramework/MIGRATION_PLAN.md` | `docs/migration/migration-plan.md` | 改定 | `confirmed` | include | 旧構成からの移行、依存及びrollback |
| `TaxonomyFramework/LEGACY_TO_TARGET_MAPPING.csv` | `docs/migration/legacy-to-target-mapping.csv` | 新規 | `confirmed` | include | 370件の旧新path対応 |
| `TaxonomyFramework/inventory/reuse-asset-assessment.csv` | `docs/migration/reuse-asset-assessment.csv` | 新規 | `confirmed` | include | 370件の機械可読評価台帳 |
| `TaxonomyFramework/LICENSE_REVIEW.md` | `docs/legal/license-review.md` | 新規 | `confirmed` | include | 308件を由来・配布単位で集約 |
| `TaxonomyFramework/REGRESSION_31_INTEGRATION_CONDITIONS.md` | `docs/testing/semantic-functional-integration-conditions.md` | 改定 | `confirmed` | include | 旧ファイル名はWORKだけで維持し、3版の機能単位統合条件を定義 |
| `TaxonomyFramework/PHASE1_PREBRANCH_PLAN.md` | `docs/migration/phase1-prebranch-plan.md` | 新規 | `confirmed` | include | 最初のcommit範囲と後続commitを固定 |
| `contracts/README.md` | `contracts/README.md` | 改定 | `confirmed` | include | contract directoryの責務 |
| `contracts/consumer-mapping-template.csv` | 同左 | 改定 | `confirmed` | include | consumer移行の空template。実データを含めない |
| `contracts/release-manifest.schema.json` | 同左 | 改定 | `confirmed` | include | release provenanceの機械検査契約 |

## 3. 最初のcommitから除外するもの

| 対象 | 理由 |
|---|---|
| `XBRL-GL-2016-PWD/**` | XBRL International原本と2025改変物が混在。公式URL参照を優先 |
| `xBRL-CSV_taxonomy/**/*.xsd`, `*.xml` | 改変版と`xbrl.org` namespaceの公開可否が未解決 |
| `specialization.py`, `graphwalk.py` | 3版の機能比較、列契約及び試験基盤の承認後に個別統合する |
| 正式FSM、BSM及びLHM | 列契約と入力来歴の承認前 |
| `taxonomy/**` | OIM最小実装commitまで生成・登録しない |
| `outputs/**`及び生成log | 再生成可能な手順と保存方針の確定前 |
| `xBRL-CSV_instance/**` | 権利、個人情報及び実取引情報の確認前 |
| `docs/ChatGPT/**`及び28件版 | 来歴資料。公開用設計文書と分離 |
| backup成果物 | 復元専用。正式repositoryへ二重登録しない |
| Framework DOCX 6冊 | ownerの公開承認と文書ライセンス確認前 |
| `docs/decisions/0003-*` | 権利未解決の旧OIM taxonomyをbaselineとして扱うため、文言再審査が必要 |
| `docs/decisions/0004-*` | generator実装の統合範囲確定後に採否を決める |

## 4. FSM→BSM→LHM/HMD基準環境のbranch及びcommit計画

branch案:

```text
rearchitecture/oim-taxonomy-2026
```

今回の準備対象は基本規則及びelement規則までとし、次の四commitを一つの再現可能な
基準環境として設計する。branch作成及びcommitは利用者承認後に別途実施する。

| # | 目的 | 入力・変更対象 | 検証 | rollback |
|---:|---|---|---|---|
| 1 | 基準仕様書と列契約 | FSM 14列、BSM 15列、LHM/HMD 17列、Class選択、semantic_path及びelement規則 | 文書link、列順、ADR、試験仕様の整合 | commit 1をrevert。mainは不変 |
| 2 | Specializationと対応試験一式 | 機能単位で統合した`specialization.py`、14列FSM fixture、15列BSM期待結果、単体・受入試験 | header、継承、削除、Association、Abstract、module-qualified Class及び決定的出力 | commit 2をrevert |
| 3 | Graph Walkと対応試験一式 | 機能単位で統合した`graphwalk.py`、15列BSM fixture、17列LHM/HMD期待結果、単体・受入試験 | 複数root、R／REF、datatype、同名Class選択、semantic_path、element及び決定的出力 | commit 3をrevert |
| 4 | 再現環境、実行手順及び検証報告 | 実行環境、依存、command、SHA-256、終了code、既知制約及び未実装事項 | clean環境で2回実行し、BSMとLHM/HMDのSHA-256一致 | commit 4をrevert |

syntax binding、profile、release manifest、taxonomy generator、taxonomy及びsampleは、
この四commitの登録と再現確認が完了するまで実装対象にしない。

旧main、tag及びbundleが復元基準であり、旧assetを新branchへ丸ごと複製しない。

## 5. branch作成直前のread-only確認

```powershell
git -C C:\Users\nobuy\GitHub\GIT\XBRL_GL_Next rev-parse --show-toplevel
git -C C:\Users\nobuy\GitHub\GIT\XBRL_GL_Next status -sb
git -C C:\Users\nobuy\GitHub\GIT\XBRL_GL_Next branch --show-current
git -C C:\Users\nobuy\GitHub\GIT\XBRL_GL_Next rev-parse HEAD
git -C C:\Users\nobuy\GitHub\GIT\XBRL_GL_Next remote -v
```

期待値:

```text
root:   C:/Users/nobuy/GitHub/GIT/XBRL_GL_Next
branch: main
HEAD:   4172d5f77c61ec7bc3ec7e68d77afb52b752bdbd
status: ## main...origin/main
```

一つでも異なる場合はbranchを作らず、差異を利用者へ報告して停止する。

## 6. 正式変更開始前の利用者判断

1. branch名`rearchitecture/oim-taxonomy-2026`を採用するか。
2. 最初のcommitで`AGENTS.md`を公開し、ローカルpathを除去するか。
3. 370件台帳をGitHubで公開する際、旧ファイル名及びSHA-256を公開してよいか。
4. 2025-12-01版XSD/XMLを公開対象外とし、公式2016 packageへの参照だけにするか。
5. 旧OIMをproject-owned namespaceで独立再実装するか、先にXBRL Internationalへ確認するか。
6. Framework DOCX 6冊の著作権者及び公開ライセンス。
7. FSM及び23 instanceの由来・匿名性確認の担当と完了基準。
8. Shared/Aligned/Distinctの古い記述が残る`docs/architecture.md`を最新定義へ直してからcommitすること。
9. sidecar schema及びcanonical `id`規則を既存FSMへ適用した検証結果。
10. FSM 14列、BSM 15列及びLHM/HMD 17列へ移行するproducer、taxonomy generator及びconsumer adapterの範囲。
11. 既存FSM／BSM／LHMの`associated_module`を推測せず確定するmappingの作成・承認担当。
12. PoC診断reportの機械可読schema、終了コード及び
    `processing_status=poc-with-errors`を受け取ったconsumerの拒否条件。
13. Specializationのsuper Class参照不能時にchildを隔離する単位。
14. module台帳及びsyntax binding対応表の正式列、保存場所及び管理者。
15. 既存FSM移行mappingの作成者、確認者及び変換不能Associationの承認手続。

## 7. 今回の操作

正式repository、UADA及びbackupは読み取りだけとした。branch作成、checkout、
正式repositoryへのコピー、commit、push、tag push、正式FSM/BSM/LHM/taxonomy生成は
行っていない。
