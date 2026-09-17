# XBRL-GL-Next Handoff
## 2026-09-15 Tax Transaction Classification and Tax Type successor adoption

- Canonical `taxonomy/accounting-entries/` and both Accounting Entries HMD placements now use the accepted 400-row successor.
- Keep `cor:taxTransactionClassification` (Purchase/Sales) and `cor:taxType` (VAT/OTH) as separate concepts. OTH covers corporate and other non-consumption taxes.
- Validation passed for deterministic generation, package closure, Tuple/OIM taxonomy entry points, and UADC PCA/EPSON formal xBRL-CSV entry points.
- Canonical promotion verified 60/60 SHA matches after backing up the 12 replaced files. Reuse the preserved evidence for unchanged premises.
- Formal GIT, commit, and push were not performed.

## 2026-08-30 Phase 1 canonical path realignment

- Canonical WORK realignment completed with 16/16 accepted input/runtime SHA matches.
- Added six accepted artefacts at approved DTS-specific paths; replaced accepted BT BSM and datatype mapping after two verified exact backups.
- Added four per-DTS publication provenance CSVs and `documents/taxonomy/README.md`.
- AE 58/58 and BT 67/67 generated taxonomy closures remain byte-identical to accepted sources. No Generator, tests, package checker, determinism, or Arelle command was rerun.
- Old generic semantic paths remain untouched as `LEGACY_PATH_DEFERRED`; they are excluded from the publication set.
- Formal GIT was read only. No copy, stage, commit, push, merge, or rebase was performed.
- Next action: review and explicitly approve the 146-row `PHASE1_FILE_LEVEL_PUBLICATION_SET.csv`, including rights and experimental-namespace publication conditions.
- Exact accepted bytes retain inherited BOM in eight semantic CSVs and the gl-gen seed XML. Before Formal Candidate approval, decide an exact-path policy exception or authorize a separate successor normalization; do not normalize the accepted baseline silently.
- Evidence: `docs/Codex/2026/202608/20260830/20260830_132849/phase1-canonical-path-realignment/outputs/`.

## 2026-08-30 split canonical DTS handoff

- Canonical WORK roots are now `taxonomy/accounting-entries/` (58 accepted files) and `taxonomy/business-transactions/` (67 accepted files).
- Every placed file matches its accepted successor-A source by relative path, size, and SHA-256; destination extras are 0 and replacements/backups were not required.
- Reuse the accepted downstream validation evidence. Do not rerun identical Generator, A/B determinism, package checker, Arelle, controlled comparison, or semantic tests without a materially changed fingerprint.
- The legacy single-tree taxonomy, including the 12 stale extras, remains untouched. Its cleanup is deferred and requires a separate decision.
- This is Canonical WORK registration only. Formal GIT/GitHub publication remains on hold. Evidence: `docs/Codex/2026/202608/20260830/20260830_103937/split-ae-bt-canonical-taxonomy-placement/outputs/`.

## 2026-08-23 Identification Scheme handoff

- Current BT HMD SHA-256: `4847717501FE9FA2305E9026F75A4FB992490D7228CA2364FEEE60F206ECB93C`.
- `BT05-02` is `Identification Scheme`; reviewed contextual local names end in `IdentificationScheme`.
- Task-local BT Completed Taxonomy passed A/B, DTS package and Arelle gates and was registered into UADC WORK.
- Do not overwrite the integrated taxonomy tree with the standalone closure without a separate integration decision.
- Review-required: align or re-designate the older `FSM.xlsx`; accepted current upstream is `FSM_btx.csv`.

更新日: 2026-08-14 (JST)

## 前回作業の結果

- 最新正式baselineは`ce18a50c67c18ac2b5df0d71c429097c210b4f80`である。
- `semantic_path` termをASCII英字へ正規化し、Association roleとassociated Classを直接連結するcanonical規則を実装した。
- 空segment、兄弟衝突、Post-Graph Walkの形式・深さ・module・親path不適合をerrorにした。
- candidate LHM、reviewed LHM、HMD 2件、manifest、Part 1、taxonomyを同期し、テスト・Arelle検証を完了した。

## 現在の注意事項

- candidate LHMはGraph Walk生成物であり、手修正しない。
- reviewed LHMでは確定済み`semantic_path`をPost-Graph Walkが修復・再生成しない。
- XPathは`module`とreviewed `local_name`から生成し、`semantic_path`から独立させる。
- WORKにはGIT baseline外の復旧資料とtaxonomy追加2件があるため、一括同期しない。

## 次の作業

1. XBRL-GL-Next、UADC_PoC、LedgerExplorerのintegration manifestを定義する。
2. 正式HMD 2件とmanifestのcommit／SHA-256をUADC_PoC入力契約として固定する。
3. UADCのBinding Tableがcanonical `semantic_path`を全件解決することを確認する。
4. UADC出力Structured CSVをLedgerExplorerのdocument／journal／settlement viewへ接続する。
5. 3プロジェクトの入力、出力、件数、SHA-256、実行コマンド、期待結果を統合検証記録へ残す。

## 未完了・未確認

- WORK taxonomyの追加2ファイルの用途は未確認。
- WORK README／inventory差分の採否は未決定。
- Arelle 2.44.1及びXMLSpy GUIは今回再実行していない。

## 2026-08-14 handoff: Detail associations

- Account Identifier is no longer owned by abstract `cor:Detail`.
- Accounting Entries exposes it only through `cor:Entry_ Detail -> cor:Detail_ Account Identifier` (`0..*`), producing 21 rows below Entry Detail in the Accounting Entries HMD.
- Business Transactions intentionally exposes no ledger Account Identifier.
- `muc:Detail_ Multicurrency`, concrete Identifier Reference, `cor:Detail_ XBRL`, the three `bus:Detail_ ...` classes, `ehm:Detail_ Serial or Lot`, `cor:Detail_ Tax`, and `lnk:Detail_ Rich Text Comment` are now explicitly composed by both concrete Detail classes.
- Transaction Detail uses `btx:Detail_ Identifier Reference`; its descendants use Detail-prefixed reviewed `local_name` values to avoid Header/Detail QName collisions.
- Abstract-association exclusions are now zero.
- `taf:Originating Document` is concrete and is inherited successfully in both HMDs.
- HMD-for-taxonomy and the 76-file generated taxonomy were regenerated. Package checker, 70 pytest tests, and four formal Arelle entry points pass.

## 2026-08-16 AGENTS.md共通統制の整備

- 目的: XBRL-GL-NextとUADC_PoCの個別指示を比較し、不足していたbackup、失敗時対応、再現性及び受入判定を共通基準へ追加し、同じ統制章をXBRL-GL-Nextへ適用する。
- 変更: WORK共通 `AGENTS.md` と XBRL-GL-Next個別 `AGENTS.md`。個別fileの既存固有条件は削除せず、共通章追加に伴い後続章番号だけを繰り下げた。
- 記録: 改訂前版は `docs/Codex/2026/202608/20260816/20260816_0549/agents-governance-harmonization/outputs/backup/` に保存した。
- 検証: UTF-8読込み、見出し順、4個別fileの共通統制章一致、改訂前後SHA-256、禁止語・必須観点、backup一致及びGit/GIT/本番非操作を確認する。
- 状態: WORK文書だけを変更。file削除、GIT側反映、stage、commit、push、外部接続及び本番操作は行っていない。

## 2026-08-16 TEST_RESULTS.md必須化

- テストを1件以上実施した変更作業では、所定task記録の `outputs/TEST_RESULTS.md` を必ず作成する規則を、WORK共通及び4個別 `AGENTS.md` へ追加した。
- 記録にはscope、日時、環境・tool/version、入力・SHA-256、設定、command、期待結果、実結果、PASS／FAIL／SKIP、error／warning、再現性、未実施事項、残存risk及び受入判定を含める。
- テスト未実施時は同fileを必須としないが、未実施理由と影響を完了報告又は本書へ記録する。
- 今回の文書検証結果は `docs/Codex/2026/202608/20260816/20260816_0701/test-results-mandatory-artifact/outputs/TEST_RESULTS.md` に保存する。

## 2026-08-19 Part 1 name / local_name / semantic_path clarification

- Formal WORK document updated: `TaxonomyFramework/XBRL_GL_Next_Taxonomy_Framework_Part_1_General_rules.docx`.
- Final SHA-256: `3A356540FB8970368E082E6DE399F74B067AEE9164D9269D65B3C5CC50AA5B4A`; verified pre-edit backup SHA-256: `76770CC8E01E84A630C7A64B679C620249D5204AF471AF1E16A86840D6D2C65D`.
- Clarified that duplicate `name` values alone are not a taxonomy conformance failure, duplicate `semantic_path` is an identity error, and duplicate (`module`, `local_name`) within an HMD is a QName collision resolved through permitted `local_name` adjustment.
- The 18-column contract, canonical semantic path, local-name/NCName rules, XPath generation, Figure 2, HMD two-file set, manifest, taxonomy entry points, and generated taxonomy were not changed.
- Document-package audit passed: 27 package parts retained; only `word/document.xml` changed; 5 media files remained byte-identical; tables 27, sections 1, and inline shapes 5 were preserved.
- Render/visual QA passed with 69 pages before and after. Graph Walk/Post-Graph-Walk, HMD generation, taxonomy generation, Arelle, and XMLSpy were not run because this was a wording-only document change.
- Review-required: `tools/XBRL_GL_Next_Detailed_Program_Specification_2026-08-16.docx` section 5.2 says approved `name/local_name` changes; it should instead state that `name` and `semantic_path` remain immutable and only approved `local_name` adjustments and permitted multiplicity restrictions are allowed. The specification was not edited because it was outside scope.
- Task evidence: `docs/Codex/2026/202608/20260819/20260819_1819/part1-name-localname-semanticpath-clarification/outputs/`.
- No delete, move, rename, Git stage/commit/push, GIT-side copy, GitHub access, external service, or production operation was performed.

## 2026-08-19 Taxonomy Generator CLI parameterisation Phase 1

- Purpose: add formal `--hmd-dir` / `--output-dir` options without changing taxonomy generation or the existing `--namespace` contract, while preserving the positional HMD and `-b` / `--base-dir` interfaces.
- Result: Phase 1 PASS. Equal old/new location specifications are accepted; conflicts, missing HMD, non-empty output, and invalid namespace are rejected explicitly.
- Regression: legacy and formal CLI outputs have the same 76-file tree and 76/76 matching SHA-256 values. Formal CLI run 2 and the dual equal-argument run are also byte-identical.
- Validation: Python compilation PASS; repository tests 76/76 PASS; old/new package checker failure 0; old/new Arelle 2.37.77 formal entry points 4/4 each with error 0 / warning 0.
- Formal inputs, 18-column contracts, semantic paths, local names, XPath values, HMDs, manifest, taxonomy generation logic, and formal taxonomy artefacts were not changed.
- Evidence: `docs/Codex/2026/202608/20260819/20260819_1916/taxonomy-generator-cli-phase1/outputs/`.
- Git/publication: no stage, commit, push, GIT-side copy, publication, or production operation.
- Next action: only after explicit user instruction, perform Phase 2 preflight for each family to confirm its canonical 18-column HMD, namespace, expected output, baseline entry points, and consumer compatibility before any implementation.
## 2026-08-19 Phase 1 Git publication

- Commit `c4a8e1e7a388328cbac2076369675f0c11676a5c` was pushed from unchanged branch `main` to `origin/main`.
- Commit scope is exactly the Phase 1 Generator CLI change, six compatibility tests, and two approved README hunks. A broader pre-existing WORK README rewrite was detected and excluded before staging.
- GIT-side Phase 1 regression reconfirmation passed in full; evidence is under `docs/Codex/2026/202608/20260819/20260819_1951/taxonomy-generator-phase1-github-publish/outputs/`.
- Existing GIT changes in `LICENSE.md`, `docs/governance/`, `docs/program_change_history.xlsx`, and `initial-upload/` remain untouched and uncommitted.

## 2026-08-20 formal XPath prefix/module分離

- `tools/taxonomy/xBRLGL_TaxonomyGenerator.py`へ反復可能な`--namespace-prefix-map PREFIX=MODULE`を追加した。EN固有分岐はなく、mapping未指定の`gl-<module>`互換とmodule namespace URI規則を維持する。
- XBRL GL Next非回帰は80/80 tests、76/76 baseline SHA一致、独立2生成一致、package checker failure 0、Arelle 4/4 error 0/warning 0でPASS。
- EN CIUSは`--namespace-prefix-map en=en16931`によりprefix障害を解消した。次の停止点は`InvoiceNumber`のsemantic datatype `Identifier`が現行共通Generator datatype契約に未登録であること。正式EN出力は0件で、Arelle、旧Taxonomy構造比較、consumer compatibilityは未実施。
- 次の一手は、旧EN baselineの型を保持するかを含む一般的semantic-datatype-to-XBRL-type契約を別レビューで確定すること。暗黙string fallback又はHMD semantic情報変更で迂回しない。
- 証跡: `docs/Codex/2026/202608/20260820/20260820_0938/taxonomy-generator-prefix-module-map/outputs/`。GIT側copy、stage、commit、push、consumer改定、旧Generator削除は行っていない。

## 2026-08-20 external datatype mapping / override

- `definitions/taxonomy/datatype_mapping.csv`と`datatype_override.csv`を追加し、共通`datatype_binding.py`からGeneratorへ接続した。semantic datatypeは変更せず、XBRL bindingだけを外部化した。
- Generatorはoverride、default、errorの決定的順序を使用する。unknown/string fallback、suffix推測、`review-required`のformal generationを禁止する。2003 legacy資産と`gl-gen`は未変更。
- XBRL GL Next非回帰は88 tests、76/76 baseline一致、独立2生成一致、package checker failure 0、Arelle正式4 entry point error 0/warning 0。
- EN HMD 164属性のうち163件を解決。BT-125 Attached documentの`Binary object`だけがreview-requiredで、EN packageは作成していない。
- 次の作業はBT-125のnormative binding決定後にexternal resourceだけを更新し、EN生成、独立再生成、Arelle、既存EN Taxonomy及びconsumer reference compatibilityを検証すること。HMD semantic datatypeを変更しない。
- 証跡: `docs/Codex/2026/202608/20260820/20260820_1402/datatype-binding-mapping-override/outputs/`。Git stage/commit/push、GIT側copy、consumer改定、旧Generator削除、既存Taxonomy上書きは未実施。

## 2026-08-20 EN CIUS Taxonomy generation

- BT-125 Attached documentは埋込みBinary Objectと確定し、external mappingを`xbrli:base64BinaryItemType`／`confirmed`へ更新した。EN coverageは164/164、review-required 0、error 0。
- 共通GeneratorからEN Tuple/OIM 13ファイルを生成。独立2生成13/13一致、QName 197/197、datatype 164/164、hierarchy/multiplicity 196/196、local reference 1,505件 unresolved 0、package failure 0、Arelle 2/2 error 0/warning 0。
- 旧Taxonomyの164 Attribute QName、109 effective datatype、13 recurring Class primary anchorを維持する一方、55 datatype binding、20 singleton Class anchor及びCanonical HMD nestingを意図的に改善した。新package defectは検出されていない。
- 旧OIM entry point `out/taxonomy/plt/en16931-oim-2026-07-05.xsd`と新OIM entry pointのpath/layoutは異なる。consumer compatibilityはHOLDで、consumerは今回変更していない。
- XBRL GL Next HMDには`Binary object`が0件で、Generator code及び他入力は不変のため88 tests、76-file回帰、Arelle 4 entry pointは再実行していない。
- 証跡: `docs/Codex/2026/202608/20260820/20260820_1431/en-cius-taxonomy-generation/outputs/`。stage、commit、push、旧Generator削除、ISO ADC/AICPA ADS作業は未実施。


## 2026-08-21 handoff: Framework Parts 1–3 canonical promotion

- The approved Part 1, Part 2, and Part 3 v3 candidates were promoted without content transformation to the canonical WORK `TaxonomyFramework/` filenames.
- Candidate, WORK canonical, and formal GIT SHA-256 values match 3/3: Part 1 `AB28B17FB1560F3A1008ACB27318F39B71CCCA5D182595992C458494DE147D9B`; Part 2 `5974DEF99D1418CFE9572573FF996400A04BADE81673B1FB792C117878E1CC95`; Part 3 `251BA08D929959665CFD23808084E1E5C74B5318F1D6B9A53F4ADA7D9E32514D`.
- Formal GIT `main` commit `fb09ff6f7cbd161a2c0c61a076e96e21973ce010` was pushed normally to `origin/main`; local and remote are 0/0 ahead/behind.
- The commit contains only the three Framework DOCX files. Pre-existing formal GIT dirty items (`LICENSE.md`, `docs/governance/`, `docs/program_change_history.xlsx`, and `initial-upload/`) remain untouched and unstaged.
- Pre-promotion WORK/GIT documents and record files are preserved under `docs/Codex/2026/202608/20260821/20260821_1017/framework-parts-canonical-promotion/outputs/backup/` with a SHA-256 manifest.
- No ToC refresh, Generator change, taxonomy change, HMD/LHM change, deletion, force push, or WORK commit/push was performed.

## 2026-08-21 handoff: local Arelle Fact Table patch

- Runtime: `C:\Users\nobuy\AppData\Local\Programs\Python\Python310\Lib\site-packages\arelle\ViewWinFactTable.py`, Arelle 2.23.1. Active patched SHA-256: `214AFE5C79A633C073CFF1861DEBC570CD42C16EF49537A9EDC9F211528293F0`.
- Rollback source retained beside the runtime as `ViewWinFactTable.original_20260821.py`, SHA-256 `15B49AF9345FE1F7ED98CB6F759B43AC6F3F8F259659F7233049E354C7B9AC76`. Patched evidence copy is also retained beside it.
- Japan PINT verification is CONFIRMED: dimension-QName collisions resolved; 23 empty leaves and 1 empty branch hidden; 32 structural parents and 141 populated rows retained; fact/context signatures unchanged; Ignore Dimensions preserved; no severe performance regression.
- Evidence: `docs/Codex/2026/202608/20260821/20260821_1032/arelle-fact-table-local-patch/outputs/`.
- No UADC, Structured CSV, metadata, taxonomy, Generator, Framework Parts 1–3, formal GIT, stage, commit, or push operation was performed.

## 2026-08-21 handoff: OIM occurrence-key Generator revision

- The authoritative common Generator now uses one root/multiplicity-based occurrence-key classifier. `d_Q` and closed-cube dimension ancestry are limited to occurrence-key Classes; singular Classes remain in the `p_Q`/`h_Q`/role/targetRole semantic hierarchy.
- Candidate acceptance passed: EN 13/13 and XBRL GL Next 76/76 independent-generation SHA matches; package checker failures 0; XBRL GL Next tests 90/90; Arelle 2.37.77 EN Tuple/OIM/Japan PINT and XBRL GL Next four entry points all error 0/warning 0.
- The XBRL GL Next WORK taxonomy was refreshed in exactly four OIM entry/definition files; Tuple and all other 72 generated files are unchanged. EN CIUS Canonical/runtime deployment was refreshed in its OIM entry and dimensional linkbase only.
- The saved Japan PINT source remains SHA-256 `1427C2DEFC363D596EDBDCC01CD9EA48927470F68C8ABE5FCEBB2276B36C9798`; 182 facts, 20 contexts, and 45 typed dimension members are unchanged. The former six ItemAttribute dimensional-invalid errors are now 0.
- XMLSpy manual confirmation is `PENDING USER`. EE 1.0 is still NOT YET IMPLEMENTED. Formal GIT, stage, commit, and push were not performed.

## 2026-08-24 BTX eight-item FSM extension precheck — review required

- The requested eight semantic capabilities were checked against the current Business Transactions and shared FSM definitions before modifying the model.
- Business Process Type, Reference Purpose, Document Attachment, a header-scoped reuse of Rich Text Comment, and a composite Adjustment have additive implementation routes. Existing Header/Detail Amount Structure and Document Type/Location are not semantic substitutes for the requested composite or discriminator facts.
- The blocking issue is Tax ownership. `btx:Header_ Tax` specializes shared `cor:Tax`; `btx:Transaction_ Detail` composes shared `cor:Detail_ Tax`, which also specializes `cor:Tax`. Adding Tax Type and distinct Tax Exemption Reason Code/Text to the reusable owner would also change Accounting Entries, contrary to the task's non-impact constraint.
- A BTX-only parallel or replacement Tax Class would require a new same-occurrence/inverse identity and compatibility decision. No current ADR or reviewed model chooses that architecture.
- The task stopped before FSM modification. Specialisation, Graph Walk, LHM review merge, post_graphwalk, HMD/taxonomy generation, UADC Binding reassessment, v3 roundtrip and all promotion operations were not started.
- No downstream test was executed because no requested model change was produced; unchanged-baseline tests would not resolve the blocking semantic ownership decision.
- Review options and evidence are recorded under `docs/Codex/2026/202608/20260824/20260824_190500/gl-btx-fsm-extension-8-items-taxonomy-binding-impact/outputs/`. The model owner must choose shared-core Tax extension, BTX concrete Tax replacement, or a linked BTX Tax extension before the ordered pipeline can resume.

## 2026-08-24 handoff: complete BTX reviewed LHM local-name-only overlay

- The latest 477-row Business Transactions candidate LHM was retained as the complete base. The prior reviewed BT subset supplied `local_name` only: 403 matched, 74 new/unmatched, 0 ambiguous; candidate-versus-reviewed non-`local_name` differences are 0 and duplicate `(module, local_name)` identities are 0.
- `Detail Tax` remains `module=btx`, `associated_module=btx`, `local_name=detailTax`, with `gl-btx:detailTax` in its taxonomy XPath.
- Official `post_graphwalk` produced a 477-row HMD (SHA-256 `6B8A5C971C569326614C96CF82FA4DE1B37CE89A500E05F8ECDE7A12F2B7F744`) with 0 errors, 0 duplicate semantic paths, and 0 duplicate QNames.
- Independent Taxonomy A/B generation matched 67/67 files by path and SHA-256. Business Transactions DTS package validation has 0 failures; Arelle Tuple and OIM entry points have 0 errors and 0 warnings.
- All previous 165 Binding `REVIEW_REQUIRED` rows were reassessed: one (`Business Process Type`) is newly reversible with the existing runtime, leaving 164. Expanded v3 has 16 rows, preserves the previous 15-row prefix, passes 6/6 focused/retained roundtrip tests, and both generated Structured CSV metadata files pass Arelle.
- Candidates and evidence are under `docs/Codex/2026/202608/20260824/20260824_195257/gl-btx-full-reviewed-local-name-only-postgraphwalk-taxonomy-binding/`. Production LHM/HMD/taxonomy/Binding were not replaced. Formal GIT, stage, commit, push, private data, and PINT JP fixtures were not used.

## 2026-09-11 V17/V14 V4連携に伴うWORK限定更新

- Canonical `datatype_binding.py`へMIT SPDX行だけを追加し、V4 SHA `A358D61C524CFE196158EABC4522586AB8F494ED6964B1BA81E60EC984EF8F8C`と一致させた。変更前SHAとbyteはUADC_PoC側の当該ChatGPT作業記録`backup/`に保持する。
- project rootに現行`LICENSE.md`は存在しないが、現行`AGENTS.md`が当該fileをMIT対象として明示し、受入済み2026-08-29 successorにMIT license本文と同一header付きfileが存在することを来歴根拠として確認した。
- Taxonomy Generatorは機能差がないため変更なし。Formal GIT、stage、commit、push、GitHub公開はNOT_PERFORMED。

## 2026-09-11 publication byte-stability handoff

- 新規Canonical `.gitattributes` SHA-256は`46ADE5AB3475862EAE83488064D63EDC972944A085F8B7571A1ABD3924F3B917`。XML/XSDをLF固定し、既公開taxonomy manifestのfilesystem SHAをplatform間で維持する。
- Accounting Entries 58件自体は変更なし。正規Generator A/B、WORK Canonical、accepted manifest、`origin/main` raw blobの全照合がPASSした。
- Formal `origin/main`には58件が既に存在する。将来のcopy対象は`.gitattributes` 1件だけであり、既存dirty worktreeを使わずfresh worktreeを用いる。
- Formal GITへのcopy、stage、commit、push、GitHub公開はNOT_PERFORMED。

## 2026-09-11 publication byte-stability promotion completed

- Commit `f30297a6148f32ce01a552f0dc3a7eb937f32fc9` was pushed normally to XBRL_GL_Next `origin/main` from accepted base `fe1d9573f86267218dff152ad2e70a4600161e99`.
- Only `.gitattributes` changed in the commit. The existing CSV rule was retained and the accepted XML/XSD LF rules were appended. The 61 other accepted resources are KEEP; the 58 split taxonomy files stayed under `taxonomy/accounting-entries`.
- Candidate/worktree/index/commit SHA continuity passed for all 100 cross-repository plan rows. MODEL/PUBLIC manifests passed 37/37; monthly references passed 12/12; local DTS unresolved references are zero; Arelle 2.37.77 passed all 14 targets with error 0 and warning 0.
- The original Formal XBRL_GL_Next checkout still has the same 58-entry dirty status set and unchanged checked-out HEAD `aa16412299b7064096cbc0935934c4cad18a4096`.
- Evidence is stored in UADC_PoC `docs/Codex/2026/202609/20260911/20260911_0932/formal-git-publication/outputs/COMPLETION_REPORT.md`.

## 2026-09-15 legacy flat taxonomy WORK registration

- The invalid mixed-namespace state in `taxonomy/` was caused by an old-namespace entrypoint coexisting with later experimental-namespace shared schemas.
- Using the original accepted WORK source recorded by Official GIT promotion `20260821_1249`, the complete 76-file old-namespace family was restored: 55 replacements and 21 existing byte matches.
- Pre-replacement bytes and SHA values are preserved under `docs/Codex/2026/202609/20260915/20260915_0905/legacy-flat-taxonomy-namespace-audit/outputs/backup/`; copy/result evidence is in the same task.
- Exact accepted validation was reused. No generation or Arelle rerun, Formal GIT modification, commit, or push occurred.
- `taxonomy/TAXONOMY_MANIFEST.csv` is a later 67-file manifest and now has 55 mismatches against the restored old-namespace family. It was preserved unchanged and requires a separate user decision.

## 2026-09-15 Stable module namespace Canonical WORK baseline

- Namespace: `https://www.xbrl.or.jp/taxonomy/xbrl-gl-next/{module}` (exact per module; version remains in file names only).
- Accepted semantics: 2026-09-04 tax transaction classification successor with `taxType` VAT/OTH and `entryDatePosted`.
- Active split DTS: Accounting Entries 58 files; Business Transactions 67 files.
- Result: deterministic generation PASS; package closure PASS; Arelle 2.37.77 error 0 / warning 0 for both DTSs and affected samples.
- Evidence: `C:\Users\nobuy\GitHub\WORK\XBRL-GL-Next\docs\Codex\2026\202609\20260915\20260915_1406\stable-namespace-work-unification\outputs\VALIDATION_REPORT.md`.
- External approval is not asserted. Official GIT and GitHub were not changed.

## 2026-09-15 AE/BT root-HMD-specific structural difference acceptance correction

- AE and BT are separately generated hierarchy expansions from different root HMDs. Exact cross-root equality of type, structure, and multiplicity is not required for same-namespace, same-name declarations.
- The tracked 14 differences are classified as `ROOT_HMD_SPECIFIC_STRUCTURAL_DIFFERENCE`; they are not conflicts, defects, or publication holds by themselves.
- Acceptance is based on conformity to each adopted root HMD, complete DTS reference resolution, and Arelle PASS from the corresponding AE or BT Tuple/OIM entry point. Existing 20260915_1406 evidence satisfies these conditions and is reused without rerun.
- The split layout and consumer entry-point selection are mandatory. Same-named files must not overwrite one another, and unconditional DTS mixing is prohibited. Single-DTS combined use is outside scope.
- No HMD commonization or multiplicity relaxation was performed. Namespace remains `https://www.xbrl.or.jp/taxonomy/xbrl-gl-next/{module}`.
- This decision supersedes descriptions that treated the 14 differences as a conflict or acceptance limitation. Other recorded BLOCKED and unresolved matters remain unchanged.
- Official GIT and GitHub operations were not performed.

## 2026-09-17 XBRL Japan namespace-only migration

- Canonical WORK now has one current project taxonomy namespace family: `https://www.xbrl.or.jp/taxonomy/xbrl-gl-next/{module}`.
- Removed the superseded `xBRL-GL2.0_btx/` tree (58 files) only after a 58-row DELETE plan, 61/61 initial backup verification, and confirmation that no required runtime dependency remained.
- Accepted Accounting Entries and Business Transactions bytes remain unchanged and match their manifests 125/125. Local taxonomy references resolve 7999/7999.
- UADC_PoC contains no current old project-namespace reference and remains aligned 22/22 to the XBRL_GL_Next authority; no UADC taxonomy copy or regeneration was required.
- Standard XBRL, XBRL Dimensions, XML, and XML Schema namespaces remain unchanged.
- Three stale test fixtures and the current documentation were updated to identify the XBRL Japan authority. The affected legacy test harness has unrelated pre-existing generator-signature/EOL failures; no unchanged failed test was rerun.
- Evidence and raw-byte backup: `docs/Codex/2026/202609/20260917/20260917_132324/xbrl-japan-namespace-migration/outputs/`.
- Formal GIT, commit, push, and external publication were not performed; publication remains a separate file-specific gate.
