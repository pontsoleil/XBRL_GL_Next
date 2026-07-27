[English](COPY_PLAN.md) | **日本語**

# コピー及びGitHub登録計画

## 1. 原則

- `UADA source`は読み取り専用の調査元とする。
- directory全体を無条件にコピーしない。
- 採用fileはsource path、destination path、size、更新日時及びSHA-256を追跡する。
- 同名fileを上書きせず、差分と採用理由を確認する。
- archive、log、cache、実データ及び権利不明の外部原本を登録しない。
- targetには`origin` remoteと専用branchがある。登録対象、公開権限及び各pushは
  別途利用者の承認を要する。

## 2. 実施済みcopy

| Source | Destination | 採否 | 衝突 | 検証 |
| --- | --- | --- | --- | --- |
| `UADA\XBRL-GL-Next\gl` | `taxonomy/tuple/gl` | 採用 | なし | 52／52 SHA-256一致 |
| core FSM／BSM／LHM | `source/models/core` | 採用 | なし | 3／3一致 |
| business transaction FSM／BSM／LHM | `source/models/business-transactions` | 採用 | FSMの空レコードをWORK側で除去 | 2／3一致、FSM 1件different |
| `UNECE`の選択CSV | `source/unece` | private分析用に採用 | なし | 9／9一致 |
| document experiment | `taxonomy/experiments/document` | private実験用に採用 | なし | 7／7一致 |
| party pool選択分 | `taxonomy/experiments/party` | 11件採用、17件非採用 | なし | 採用11件一致 |
| code-list選択分 | `taxonomy/experiments/codelists` | 8件採用、111件非採用 | なし | 採用8件一致 |
| semantic／taxonomy tool | `tools` | 4件採用 | specializationをWORK側で改訂 | 3／4一致、specialization 1件different |
| vendor invoice CSV／JSON | `examples/vendor-invoice` | 2件採用 | なし | 2／2一致 |
| `xBRL_GL2.0_2026-01-06\xBRL-GL2.0_btx` | `xBRL-GL2.0_btx` | source 57件を採用し日付正規化。WORKで`PROVENANCE.md` 1件を追加し現在58件 | project treeとして別管理 | source 57件、追加1件、entry point validation |

file-level import evidenceはWORK生成台帳です。この文書登録単位には含めず、
linkを満たす目的だけでコピーしません。

## 3. 今回追加するPhase 0成果物

| Source | Destination | 理由 | 検証 |
| --- | --- | --- | --- |
| repository、UADA及び公式packageのread-only scan | `TaxonomyFramework/INVENTORY.md`と`inventory/*` | provenanceと登録区分の固定 | manifest summary、hash再計算 |
| XSD/XML dependency scan | `TaxonomyFramework/DEPENDENCIES.md` | DTS graphと欠落参照の固定 | XML parse error 0 |
| phase判定 | `TaxonomyFramework/OPEN_ISSUES.md` | blockerの責任と次phaseを明示 | IDと処置をreview |
| copy結果 | `TaxonomyFramework/COPY_PLAN.md` | 採否、衝突、検証を記録 | source comparison 99件（97件同一、WORK側改訂2件） |
| manifest generator | `tools/inventory/generate_phase0_manifests.py` | 再現可能な棚卸し | Python compileと再生成比較 |

## 4. `xBRL-GL2.0_btx`とOIM prototypeの配置整理案

本節は移動・削除前の提案である。利用者の確認を受けるまで、ファイルの移動、削除、
名称変更、上書き又は正式GITへのコピーを行わない。

### 4.1 調査結果

| 項目 | `xBRL-GL2.0_btx/` | `taxonomy/oim/prototype/` |
|---|---:|---:|
| 全ファイル | 58 | 46 |
| XSD | 19 | 19 |
| XML | 28 | 27 |
| その他 | 11 | 0 |
| 0 byteファイル | 0 | 0 |

source側を再集計した結果は57ファイル、WORK側は58ファイルである。差分1件は
WORKでimport記録として作成した`PROVENANCE.md`であり、source側には存在しない。
したがって「57件採用」はsource payloadの件数として正しく、現在配置の総数は58件である。

追加1件の`PROVENANCE.md`はsource payloadではなく、import後にWORKで作成した
provenance文書です。source側に存在しないこと、WORK SHA-256及び記載source roleを
確認しています。

`taxonomy/oim/prototype/`の46ファイルは、相対path及びSHA-256が
`xBRL-GL2.0_btx/`内の46ファイルと全件一致する。したがってtaxonomy本体を
両方で継続管理する必要はない。

46件には、entry pointから名称参照されない比較用ファイル
`plt/plt-def-2026-12-31_02-20_A.xml`及び
`plt/plt-def-2026-12-31_02-20_B.xml`が含まれる。これらを正式DTS構成へ含めるか、
比較fixtureへ分離するかは未決である。

### 4.2 `xBRL-GL2.0_btx/`だけにある12件

| 区分 | ファイル | 配置案 | 現在の処置 |
|---|---|---|---|
| provenance | `PROVENANCE.md` | `docs/provenance/oim-prototype-import.md`又はsource manifest | 保持 |
| 比較用copy | `vendor_invoices copy.json` | 登録対象外又は`tests/fixtures/comparison/` | 保留 |
| sample source候補 | `vendor_invoices.csv` | `examples/vendor-invoice/`又は`tests/fixtures/instance/` | 既存exampleとの差分確認 |
| sample生成物候補 | `vendor_invoices.json`、`xbrl-gl.json` | 再生成手順確定後に`examples/`又は`outputs/` | 保留 |
| binary生成物候補 | `vendor_invoices.xlsx`、`xbrl-gl_skeleton.xlsx` | 原本性を確認。生成物ならGit対象外 | 保留 |
| metadata source候補 | `xbrl-gl_skeleton.csv` | `tests/fixtures/metadata/` | 保留 |
| 検証tool候補 | `verify_tax_subtotals*.py` 3件 | `tests/`又は`tools/validation/`へ機能統合 | 保留 |
| 比較instance | `ids/Vendor_Invoices_revised.xml` | `tests/fixtures/legacy-instance/`又は参照のみ | 保留 |

`examples/vendor-invoice/`には同名のCSV及びJSONがあるが、上記ファイルとは
SHA-256が一致しない。上書きせず、fact、metadata、taxonomy URI及び生成元の差分を
確認する。

### 4.3 提案する将来配置

| 資産 | 正本候補 | 重複側の将来処置 | gate |
|---|---|---|---|
| OIM／Palette taxonomy本体 | `taxonomy/oim/prototype/` | `xBRL-GL2.0_btx/`内の同一46件はmanifest確認後に除去候補 | XML Schema、DTS、XMLSpy、Arelle及び全SHA一致 |
| definition比較A／B | `tests/fixtures/taxonomy-comparison/`又は除外 | taxonomy正本から分離候補 | 比較目的と期待差分の文書化 |
| sample instance／metadata | `examples/`又は`tests/fixtures/` | source bundle直下から分離候補 | 権利、匿名性、生成元、期待値 |
| 再生成可能なJSON／XLSX | `outputs/`又はGit対象外 | source bundle直下から分離候補 | 生成commandとSHA再現 |
| validation script | `tests/`又は`tools/validation/` | 3実装を機能比較後に統合 | unit test、CLI、依存関係 |
| import provenance | `docs/provenance/`とmanifest | 旧bundle pathは記録だけ保持 | source、変換、日付、SHA |

### 4.4 空ファイルの扱い

今回の2ディレクトリには0 byteファイルはない。今後検出した場合は削除せず、次に分類する。

1. 意図的なplaceholder：`.gitkeep`等へ目的を明記。
2. generatorの異常出力：`outputs/quarantine/`相当として登録対象外。
3. 内容欠落：source hashと生成logを確認し、再取得又は再生成。

## 5. 今後コピーしないもの

| 対象 | 判断 | 理由 |
| --- | --- | --- |
| 公式XBRL GL 2015／2017 ZIP | repositoryへコピーしない | 公式URL、version及びhashで再取得可能。外部packageをproject packageへ混在させない |
| UADAのarchive、dated work folder及びduplicate Excel | コピーしない | provenanceを曖昧にし、再生成可能なCSVと重複する |
| UADAのlog、`__pycache__`及びbytecode | コピーしない | 一時又は生成物 |
| UN/CEFACT原本及び大量code list | 許可確認までコピーしない | 再配布・派生物公開条件が未確定 |
| consumer repositoryのLHM／実データ | コピーしない | checksumとcrosswalkだけをprovider側で管理する |
| `docs/ChatGPT`の原本Excel | release packageへコピーしない | review evidenceであり配布物ではない |

## 6. GitHub tracking候補

remote未設定のため、次は「登録候補」であってpush承認ではありません。

### tracking候補

- `AGENTS.md`、`README.md`、`.gitignore`
- `docs`のproject-authored文書とADR
- `TaxonomyFramework`のproject文書及びPhase 0台帳
- `contracts`、`integration`及び`tests`
- license表示を確認したtool

### private repository限定でtracking

- `source/models`
- `taxonomy/tuple`
- `taxonomy/oim/prototype`（重複46件、比較A／B及びライセンスの整理後）
- `taxonomy/experiments`
- `source/unece`
- `examples`
- `docs/ChatGPT`

`xBRL-GL2.0_btx/`全体はtracking候補にしない。taxonomy本体、sample、tool、生成物及び
provenanceを前節の責務別配置へ分け、承認されたファイルだけを個別に候補化する。

### public push対象外

- XBRL由来で公式namespaceを使用する改変taxonomy
- permissionが確認できないUN/CEFACT派生material
- license未記録tool
- binary review evidence、archive、cache及びlog

## 7. コピー後の検証

```powershell
python .\tools\inventory\generate_phase0_manifests.py `
  --repo . `
  --source $env:XBRL_GL_NEXT_UADA_SOURCE `
  --official-dir $env:XBRL_GL_OFFICIAL_PACKAGE_DIR `
  --work-root $env:XBRL_GL_NEXT_WORKSPACE `
  --output-dir .\TaxonomyFramework\inventory

python .\tests\check_repository.py
python -m py_compile .\tools\inventory\generate_phase0_manifests.py
git diff --check
```

taxonomyを変更する場合は、これらにArelle及びXMLSpyのentry point検証を追加します。
コピー時点で原本と同一だった`tools/semantic/bie_specialization.py`は、
Phase 1のP0-17としてWORK側で修正した後、`tools/semantic/specialization.py`
へ名称変更し、unit test及びCLI testを追加しました。

## 8. semantic tool統合前の確定方針

### 8.1 canonical core

- FSMは14列、BSMはFSM 14列＋末尾`id`の15列とし、BSMに`element`を持たせない。
- LHM/HMDは同じ17列契約とし、`semantic_path`、`associated_module`及び
  HMD単位判定用`class_term`を保持する。`path`、`associated_class`、
  `abbreviation_path`及び`xpath`は除く。
- `xpath`が必要ならsyntax bindingで管理する。
- elementはsemantic path確定後にprefixなしのlowerCamelCase NCNameとして生成し、
  親・先祖segmentを重複なく追加してmodule内で一意にする。連番、入力順及びhashは
  使用しない。C、A及びREFは必須、Rはmultiplicity上限が1なら空欄、上限が1を
  超える又は無制限ならdimension用elementを必須とする。
- FSM／BSMでは異なるmoduleの同名Classを候補として保持できるが、一つのHMDでは
  同じ`class_term`について一つのmoduleだけを明示選択し、混在させない。

### 8.2 DNM

DNM及び`graphwalk.py -o`は今後サポートしない。後続の実装段階でDNM用option、
生成分岐、専用出力、使用例、help及びDNM専用testを削除対象とする。今回は
programを変更しない。

### 8.3 WORK版18列の追加項目

`fsmid`、`inherited`、`UNID`、`TDED`、`context`及び`short_name`は16列coreへ
追加せず、provenance、inheritance trace、external reference、semantic context及び
label／presentationのsidecarへ分離する。列、型、join key、多重度、欠落・重複時の
動作及びmanifest案は`SEMANTIC_MODEL_COLUMN_CONTRACTS.md`で定義する。

### 8.4 Association

空roleは空欄のまま許容し、推測又は生成しない。同一Class内に同じ
`(property_term, associated_module, associated_class)`を持つAssociationが複数あれば、
property_type、multiplicity、ID又はsequenceが異なっても重複入力エラーとして報告する。
PoCではモデル全体を停止せず、一意なClass／propertyを処理してBSMを生成し、曖昧な
propertyを未反映又は要確認として診断reportへ記録する。ID又は入力順による選択、
暗黙統合、role書換え又は連番による回避を行わない。BSMの処理状態は15列へ追加せず、
manifestの`processing_status`、件数及び`report_file`で管理する。

## 9. Phase 0 exit decision

copy対象、非採用対象、参照のみ、private限定及びpublic holdを区分しました。
したがって棚卸しと登録範囲の確定は完了です。public GitHub releaseは
[`OPEN_ISSUES_ja.md`](OPEN_ISSUES_ja.md)のpublication blockerを解消し、
利用者がvisibility、publication authority及び登録対象を承認した後に行います。

## 10. FSM→BSM→LHM/HMD基準環境の登録準備

基本規則及びelement規則までの登録対象、除外対象、要確認対象、ライセンス、
実データ・秘密情報、配置及び四commit案は
`TaxonomyFramework/PRIVATE_GITHUB_BASELINE_REGISTRATION_PLAN.md`はtargetに
日本語のみの作業文書として既に存在します。英語正本ではないため、英語正本及び
整合する日本語版を作成するまで、正本への昇格及び後続展開を保留します。

現行WORK版、単独4件版及び28件版はいずれも機能比較元であり、そのまま採用しない。
新14／15／17列契約に対応するprogram、合成fixture、期待結果及び試験を一式として
検証した後に登録候補へ昇格する。利用者確認前に正式GITへのコピー、branch作成、
commit又はpushを行わない。
