# XBRL-GL-Next Current Baseline
## 2026-09-15 Tax Transaction Classification and Tax Type successor baseline

- The canonical Accounting Entries successor is based on the validated 2026-09-04 taxonomy and adds the distinct `cor:taxType` concept from the UADC authoritative HMD.
- `cor:taxTransactionClassification` represents Purchase/Sales. `cor:taxType` represents VAT/OTH; OTH is retained for corporate and other non-consumption taxes.
- The 400-row accepted HMD has SHA-256 `CE7FDCB8013CCDB2CF2513107F972F174ACC0BBA5207EEB12DE206DC0B08F500` and uses `cor:entryDatePosted`.
- Validation passed: two-run determinism 58/58, package failures 0, Arelle 2.37.77 Tuple/OIM errors 0 and warnings 0, plus UADC PCA/EPSON formal xBRL-CSV errors 0 and warnings 0.
- Canonical WORK registration covered 58 taxonomy files and two HMD placements: REPLACE 12, KEEP 48, verified 60/60 by SHA-256.
- Evidence: `docs/Codex/2026/202609/20260915/20260915_1101/adopt-20260904-tax-classification-baseline/outputs/successor-tax-type/`.

## 2026-08-30 Phase 1 canonical semantic/taxonomy publication tree

- Accepted Phase 1 semantic inputs now use DTS-specific canonical paths under `semantic-model/LHM/accounting-entries/`, `semantic-model/LHM/business-transactions/`, `semantic-model/HMD/accounting-entries/`, and `semantic-model/HMD/business-transactions/`.
- Accepted BT BSM SHA-256 is `A1EA5FAA47B27CB59FEE61B9E07A0053CFF9AF5B148FAE4010B42A64761D5B52`; accepted datatype mapping SHA-256 is `387940F7E0E1AED32145BB37DEA2F1153D226E2971B5A947A9CCB0A280C42193`.
- Accepted static seed is `tools/taxonomy/gen/gl-gen-2026-12-31.xsd`, SHA-256 `F74A3064EAEDE670D77B167096BA7486D04FD28559839BF016E7D379CE447106`.
- `taxonomy/accounting-entries/` remains 58/58 accepted files and `taxonomy/business-transactions/` remains 67/67 accepted files, byte-unchanged.
- Per-DTS publication provenance is under `taxonomy/provenance/`; split architecture documentation is under `documents/taxonomy/README.md`.
- `docs/**`, `ids/**`, and the legacy single-tree taxonomy are excluded from the Phase 1 publication set. Formal GIT publication remains pending file-level authorization.
- Evidence: `docs/Codex/2026/202608/20260830/20260830_132849/phase1-canonical-path-realignment/outputs/`.

## 2026-08-30 Split Accounting Entries / Business Transactions canonical DTS

- Accounting Entries の accepted successor-A 58 files を `taxonomy/accounting-entries/` に、Business Transactions の accepted successor-A 67 files を `taxonomy/business-transactions/` に byte-for-byte 配置した。
- Accounting Entries source run は `20260830_094307/accounting-entries-xbrl-or-jp-successor`、HMD SHA-256 は `DB0495A4F836751ECFFC5B759BD4F7AA8AF4002BD725758FCFAB3BE61E03CF5E`。
- Business Transactions source run は `20260830_082547/xbrl-or-jp-publication-successor-technical-validation`、HMD SHA-256 は `6B8A5C971C569326614C96CF82FA4DE1B37CE89A500E05F8ECDE7A12F2B7F744`。
- 両DTSは accepted successor Generator SHA-256 `69C47F1134389ADB4405BD9F898718B43F76D2552F3CCD61898E23C5D5325B02` の既存technical PASSを継承する。今回、Generator、determinism、package checker、Arelle、semantic testは再実行していない。
- 旧single-tree taxonomy 83 filesと12 stale extrasは変更せず、cleanupはdeferred。Formal GITへのcopy、stage、commit、pushは未実施。
- Placement evidence: `docs/Codex/2026/202608/20260830/20260830_103937/split-ae-bt-canonical-taxonomy-placement/outputs/`。

## 2026-08-23 Business Transactions Registered Identifier terminology

- Accepted FSM CSV identity `BT05-02` is `Identification Scheme`; BSM 737 rows, raw BT candidate 441 rows, reviewed LHM 801 rows.
- BT HMD has 403 rows and SHA-256 `4847717501FE9FA2305E9026F75A4FB992490D7228CA2364FEEE60F206ECB93C`; AE HMD SHA remains `DB0495A4F836751ECFFC5B759BD4F7AA8AF4002BD725758FCFAB3BE61E03CF5E`.
- Standalone BT Taxonomy A/B is 67/67 deterministic, package failures 0, Arelle 2.37.77 Tuple/OIM errors/warnings 0/0.
- Evidence: `docs/Codex/2026/202608/20260823/20260823_1552/registered-identifier-identification-scheme/outputs/`.

記録日: 2026-08-14 (JST)

## Git baseline

- branch: `main`
- upstream: `origin/main`
- code baseline commit: `ce18a50c67c18ac2b5df0d71c429097c210b4f80`
- subject: `Fix semantic path normalization and update Part 1`
- 記録時点のahead/behind: `0/0`
- 本文書を追加するdocumentation commitは自己参照を避けるため固定値として記録しない。最新値は`git rev-parse HEAD`で確認する。

## 正式入力

|相対パス|用途|SHA-256|
|---|---|---|
|`semantic-model/LHM/LHM_candidate.csv`|Graph Walk candidate LHM|`7679BAA3BEC60B187ACD033239FF6D3B1A2CC3092171A7F3FFEA07F7B2694721`|
|`semantic-model/LHM/XBRL_GL_Next_LHM_reviewed.csv`|設計者reviewed LHM|`ECDBE773CCB6408BFE702AAAF495F56049FEFB4D0A1A14D72FAB142BB8A87FB9`|
|`semantic-model/LHM_for_taxonomy/XBRL_GL_Next_HMD_AccountingEntries_for_taxonomy.csv`|Accounting Entries HMD|`E9481DAF7A3403771FCD9F67FC078229354CEE697A7199F0943AA883648D4B29`|
|`semantic-model/LHM_for_taxonomy/XBRL_GL_Next_HMD_BusinessTransactions_for_taxonomy.csv`|Business Transactions HMD|`A1FE079A36EB38D15911BFDE28A37FBF6470767E349FC4241AC8D632EF1D70CA`|
|`semantic-model/LHM_for_taxonomy/manifest.csv`|正式HMD manifest|`7E96458955EB8123031D47E3039D9ECD6B06F687BB2D6AD111E5C16C52807BBA`|

正式処理経路はFSM → Specialisation → BSM → Graph Walk → candidate LHM → human review → Post-Graph Walk → HMD → Taxonomy Generatorである。

## 正式成果物と実装

- taxonomy: 56生成ファイル
- Tuple entry point: Accounting Entries、Business Transactions
- OIM entry point: Accounting Entries、Business Transactions
- sample instance: Tuple 2件、OIM 2件

|相対パス|SHA-256|
|---|---|
|`tools/semantic/graphwalk.py`|`2CFC9F6868D04E173B6752E2AB4A1A4B18038AAE010A1AEB0E136ECE5068CD0E`|
|`tools/semantic/post_graphwalk.py`|`985D217CB150C7A00181BC3D0AC9DF8350DC458A2E09C3310FC110024E944DA7`|
|`tools/taxonomy/xBRLGL_TaxonomyGenerator.py`|`205FD43B730993C573ED55228FA4E01BE490A17CC1177EACDD9A995E2AA05447`|
|`TaxonomyFramework/INVENTORY.md`|`0CB113FDA72D10227CF16A2A84C79730D5994D9796701F1E644B85CDAB7BF2F5`|

## 検証済み条件

commit `ce18a50...`の受入記録:

- Graph Walk／Post-Graph Walk／semantic pipelineを含む全テスト70件成功
- taxonomy 56ファイルの再生成一致
- repository checker failure 0、未解決file 0、未解決fragment 0
- Arelle 2.37.77: taxonomy entry point 4件及びinstance entry point 4件でerror 0、warning 0
- canonical `semantic_path`、18列契約、reviewed `local_name`／XPathを維持

上記は既存baselineの検証記録であり、今回の3文書作成時には再実行していない。

## WORK差分

- 正式semantic LHM/HMD、manifest、主要3実装はGIT baselineとSHA-256一致。
- WORKのREADME及び`TaxonomyFramework/INVENTORY.md`はGIT baselineと異なる。
- WORKのtaxonomyは58ファイル、GIT正式baselineは56ファイル。追加2件を正式成果物とみなさず、別途差分確認する。
- WORKには復旧した`docs/ChatGPT/`及び`docs/Codex/`等の未追跡資料があるため、一括同期しない。

## 2026-08-14 concrete Detail association baseline

- `cor:Account Identifier` was removed from the abstract `cor:Detail`.
- `cor:Entry_ Detail` retains an explicit Composition to `cor:Detail_ Account Identifier` (`0..*`).
- `btx:Transaction_ Detail` intentionally contains no Account Identifier because Business Transactions messages do not carry ledger account codes.
- The other nine abstract Detail compositions were moved to explicit concrete `Detail_ ...` compositions on both Entry Detail and Transaction Detail; the abstract self-reference was removed without creating a recursive concrete reference.

## 2026-08-16 AGENTS.md運用統制baseline

- WORK共通 `AGENTS.md` SHA-256: `649475023BC0226FAC8BE7835CD588B24212EAA1320C3B91370EC90D7418322A`
- XBRL-GL-Next個別 `AGENTS.md` SHA-256: `753BAA185FA40F7750C81FD25D09E11A6142235D45DE36857076953319FD0756`
- 4プロジェクト共通の個別章として、開始前確認、変更範囲、禁止事項、安全策、成果物・log・記録、backup・復旧、失敗時対応、test、再現性、受入判定、Git運用及び終了checkpointを固定した。
- WORK側既存fileの削除は実対象の個別指定がない限り禁止し、WORK変更、GIT反映、stage、commit、push、外部接続及び本番操作を別承認とする。
- 今回は運用文書だけを変更し、code、正式model/data、公開成果物、GIT側、本番baselineは変更していない。
- テストを1件以上実施する変更作業では、所定task記録の `outputs/TEST_RESULTS.md` を必須成果物とする。
- Rows: FSM 499, FSM_btx 86, BSM 732, candidate LHM 833, reviewed LHM 831, Accounting Entries HMD 398, Business Transactions HMD 433.
- Existing reviewed `name`, `local_name`, and `multiplicity` values were retained by `semantic_path`; the two previous candidate exclusions remain excluded.
- Current hashes: FSM.xlsx `C8259F330911FB923BE5D9952870BFFCAE806C18D99993B8E8AF51648EF8F731`; BSM `28BC31EB98DB7F8D50FA376EF89138CDB0FCFCBB89A2B7CFCDA034DC4DB7CE86`; candidate `FF153C83629A4AE81EED2DCBFE97E6B95C6C9526013F505ADECF7808E3A9EDFA`; reviewed `ED7FCB39664C76299BAF29F923B1CE1615658264AB02F29E8198A3154D534BEF`.
- HMD hashes: Accounting Entries `0730006AAA1F84C9E14F1347BF134F40A02A9F0B660A34849F465F57C8509E2A`; Business Transactions `49D54DF6536E37C3911650535E33F55AC5F6FA6E3ED620D6AC355E8ED318BE01`; manifest `9F940D302AFE041CFF3299258A6A28A0EF5077230546F8F554099CC7DC93C605`.
- Taxonomy contains 76 generated files plus two retained Markdown README files. Two independent generations were byte-identical; the package checker and four Arelle entry-point validations passed with zero errors and warnings.

## 2026-08-19 Part 1 naming clarification WORK baseline

- `TaxonomyFramework/XBRL_GL_Next_Taxonomy_Framework_Part_1_General_rules.docx` was clarified without changing the semantic or taxonomy processing architecture.
- Current WORK SHA-256: `3A356540FB8970368E082E6DE399F74B067AEE9164D9269D65B3C5CC50AA5B4A`.
- LHM `name` is a human-readable semantic occurrence name and is not required to be globally unique; `semantic_path` is occurrence identity; `local_name` is the taxonomy implementation name; QName uniqueness is determined from namespace (`module`) and `local_name` within the applicable HMD.
- Taxonomy-only collisions are resolved through permitted `local_name` review adjustments, not by changing `name`. A genuine semantic-name defect is corrected at its source or governing generation rule and regenerated.
- The 18-column contract, canonical `semantic_path`, reviewed `local_name`, XPath construction, Figure 2, HMDs, manifest, taxonomy artefacts, and entry points remain unchanged.
- This is a WORK-only document state. No GIT-side copy, stage, commit, push, or GitHub operation was performed.

## 2026-08-19 Taxonomy Generator CLI Phase 1 WORK baseline

- `tools/taxonomy/xBRLGL_TaxonomyGenerator.py` now formally supports `--hmd-dir` and `--output-dir`; positional `lhm_for_taxonomy`, `-b` / `--base-dir`, and the existing required `--namespace` contract remain supported.
- Generator SHA-256 changed from `205FD43B730993C573ED55228FA4E01BE490A17CC1177EACDD9A995E2AA05447` to `968D45BCFC244A277C5CF7625A9E0C8746AFF02B3781D9FFD795B922EB724FC4`.
- Generator class and `generate_formal_hmd_package` AST are unchanged; only CLI parsing and old/new location resolution changed.
- Formal HMD and manifest hashes remain unchanged.
- Legacy and formal CLIs each generated the same 76-file package; all relative paths and SHA-256 values match. A second formal generation is identical, package checker failures are zero, 76 tests pass, and Arelle 2.37.77 validates all four entry points for each output with error 0 / warning 0.
- Phase 1 is PASS. Phase 2 was not started. This is WORK-only; no stage, commit, push, or GIT-side copy was performed.
## 2026-08-19 Taxonomy Generator CLI Phase 1 Git baseline

- Canonical GIT `main` and `origin/main` now point to commit `c4a8e1e7a388328cbac2076369675f0c11676a5c` (`taxonomy: parameterize HMD and output directories`).
- The commit contains only `README.md`, `tools/taxonomy/xBRLGL_TaxonomyGenerator.py`, and `tests/test_v5_taxonomy_generator.py`.
- GIT-side reconfirmation passed: 76/76 unit/regression tests; legacy/formal CLI output 76/76 byte-identical; second formal generation identical; both package checks failure 0; Arelle 2.37.77 old/new four entry points each error 0 / warning 0.
- Local `HEAD`, `origin/main`, and remote `refs/heads/main` were verified equal after push.

## 2026-08-20 XPath prefix/module mapping WORK candidate

- 共通Generatorへ一般的な`--namespace-prefix-map PREFIX=MODULE`を追加し、HMD module identityとXPath lexical prefixを分離した。Generator SHA-256は`8476257E6F0D2928D7BE1A0C97060119D2D42DB9FE8D06A8116EF5B740D6945B`。
- mapping未指定の`gl-cor`、`gl-bus`、`gl-btx`等は従来どおり解決する。XBRL GL Next回帰は80/80 tests、既存baselineとの76/76 SHA一致、独立2生成一致、package checker failure 0、Arelle 4 entry point error 0/warning 0。
- EN CIUSの`en=en16931`解決はPASSしたが、完全生成は現行Generatorがsemantic datatype `Identifier`を拒否してHOLD。prefixとは独立したdatatype契約のreviewが必要で、EN Taxonomy成果物は生成していない。
- WORK-only candidateであり、GIT側、stage、commit、push、既存正式taxonomy及びconsumerは変更していない。

## 2026-08-20 external datatype binding WORK candidate

- Canonical HMDのsemantic `datatype`とXBRL item typeを分離し、48行の`datatype_mapping.csv`と2行の`datatype_override.csv`を正式resource候補として追加した。
- 共通Generatorはexplicit override、datatype default、errorの順で解決し、unknown、`review-required`、string fallback及び`name`/`local_name`末尾推測を拒否する。EN固有分岐、namespace URI規則、`gl-gen`及びTaxonomy構築logicは変更していない。
- XBRL GL Nextは88 tests、既存baselineとの76/76 SHA一致、独立2生成一致、package checker failure 0、Arelle 4/4 error 0/warning 0で非回帰PASS。
- EN CIUS Canonical HMDはSHA-256 `E4C43D010BD853A3A70195C6DCB9BE4A4F0EAD6FAD5D1C8825D202BDC538CACA`を維持。164属性中161 default、2 overrideを解決し、BT-125 `Binary object` 1件を`review-required`として生成前に停止した。
- 証跡: `docs/Codex/2026/202608/20260820/20260820_1402/datatype-binding-mapping-override/outputs/`。WORK-onlyであり、stage、commit、push、consumer改定、旧Generator削除及び既存Taxonomy上書きは行っていない。

## 2026-08-20 EN CIUS common-Generator package WORK candidate

- CEN/TS 16931-3-2のBT-124/BT-125区別に基づき、`Binary object` mappingを`xs:base64Binary`／`xbrli:base64BinaryItemType`／`confirmed`へ確定した。mapping SHA-256は`740C8A45EAD0EBF6816D3D67C0FACDCACBB58D5273EF168C1DE470AA16A3AFFB`。
- Canonical HMD SHA-256 `E4C43D010BD853A3A70195C6DCB9BE4A4F0EAD6FAD5D1C8825D202BDC538CACA`、`module=en16931`、XPath `en:`及び`--namespace-prefix-map en=en16931`を維持し、EN datatype 164/164を解決した。review-required 0、error 0。
- 共通GeneratorはTuple/OIM 13ファイルを独立2回生成し、13/13 SHA一致。QName 197/197、hierarchy/multiplicity 196/196、datatype 164/164、package checker failure 0、Arelle 2 entry point error 0/warning 0。
- 旧EN Taxonomyとの差はlegacy compatibility、intentional improvement、defectへ分類し、新package defectは0。旧entry-point pathを参照するconsumerは互換性reviewが残る。
- 証跡: `docs/Codex/2026/202608/20260820/20260820_1431/en-cius-taxonomy-generation/outputs/`。WORK-onlyであり、既存Taxonomy、consumer、旧Generator、ISO ADC/AICPA ADS及びGit状態を変更していない。


## 2026-08-21 Framework Parts 1–3 canonical promotion

- The reviewed Parts 1–3 candidates were promoted byte-for-byte to the canonical WORK paths under `TaxonomyFramework/`.
- Part 1 SHA-256: `AB28B17FB1560F3A1008ACB27318F39B71CCCA5D182595992C458494DE147D9B`.
- Part 2 SHA-256: `5974DEF99D1418CFE9572573FF996400A04BADE81673B1FB792C117878E1CC95`.
- Part 3 SHA-256: `251BA08D929959665CFD23808084E1E5C74B5318F1D6B9A53F4ADA7D9E32514D`.
- The same three files were copied to formal GIT and published to `origin/main` in commit `fb09ff6f7cbd161a2c0c61a076e96e21973ce010` (`Update XBRL GL Next Taxonomy Framework Parts 1-3`).
- Candidate files and Codex evidence remain preserved. ToC fields were not refreshed. Generator, taxonomy, HMD/LHM, and implementation artefacts were not changed.

## 2026-08-21 local Arelle Fact Table patch baseline

- The PATH-resolved Python-package Arelle runtime is `arelle-release 2.23.1` under Python 3.10. Its active `ViewWinFactTable.py` was locally patched for dimension-aware column identity and empty-row/subtree filtering.
- Original and same-directory backup SHA-256: `15B49AF9345FE1F7ED98CB6F759B43AC6F3F8F259659F7233049E354C7B9AC76`. Patched active and same-directory evidence SHA-256: `214AFE5C79A633C073CFF1861DEBC570CD42C16EF49537A9EDC9F211528293F0`.
- The unchanged Japan PINT xBRL-CSV loaded with 182 facts and 20 contexts. Fact signature `1369E8ADE33105BD14D2B3958E74D0E15347D01784FA124146559E1D7A197D85` and context signature `92646F217FC28DE3E61F8A4B327ECF9BD1444A816F0B9FCADD53BC7258AC9B19` matched before/after.
- This is a local Arelle GUI display patch only. UADC, Structured CSV, metadata, taxonomy, Generator, Framework Parts 1–3, formal GIT, and GitHub baseline are unchanged.

## 2026-08-21 OIM occurrence-key Generator WORK baseline

- `tools/taxonomy/xBRLGL_TaxonomyGenerator.py` now classifies the HMD root and non-root `0..*`/`1..*` Classes as occurrence-key Classes. Non-root `0..1`, `1`, and `1..1` Classes retain `p_Q`, `h_Q`, roles, and targetRole traversal but no longer receive `d_Q`.
- Closed cubes now contain only the ordered occurrence-key Class lineage. Tuple output is byte-unchanged; the XBRL GL Next generated change scope is four OIM entry/definition files only.
- Generator SHA-256: `9890946AEF8DD06C5B363605E6E951C27007C6932B4D0B3FB3C70807391BE651`. Unit/regression tests pass 90/90; two independent 76-file generations match 76/76; package checker failure 0; Arelle 2.37.77 validates four entry points with error 0/warning 0.
- EN CIUS `ItemAttributes` uses exactly `dInvoice`, `dInvoiceLine`, and `dItemAttributes`; `dItemInformation` is absent. The unchanged saved Japan PINT instance validates with error 0/warning 0, and the accepted 19-case forward/reverse/metadata/semantic regression passes 19/19 with semantic differences 0.
- EE 1.0 generation remains NOT YET IMPLEMENTED. Formal GIT, stage, commit, and push were not changed. Evidence: `docs/Codex/2026/202608/20260821/20260821_1119/oim-occurrence-key-generator-revision/outputs/`.

## 2026-09-11 datatype binding license-header Canonical WORK baseline

- `tools/taxonomy/datatype_binding.py`に`SPDX-License-Identifier: MIT`を追加した。根拠は本project `AGENTS.md`の明示指定、既存MIT header群、及び受入済みsuccessorの`LICENSE.md`と同一header付きfileである。
- ASTは変更前後で同一であり、機能変更ではない。`xBRLGL_TaxonomyGenerator.py`はV4候補との差が文字正規化だけであるため変更していない。
- Formal GIT、commit、push、GitHub公開は実施していない。

## 2026-09-11 taxonomy publication byte-stability baseline

- Accounting Entries split successor 58件を正規Generatorから2回再生成し、現行Canonical及び`origin/main` commit `fe1d9573f86267218dff152ad2e70a4600161e99`のraw Git blobと58/58一致した。
- `.gitattributes`をCanonical WORKへ追加し、`*.xsd text eol=lf`及び`*.xml text eol=lf`でtaxonomy manifestのSHAをOS非依存にした。task-local cloneの`core.autocrlf=true`検査でもOIM entrypoint SHAは一致した。
- これはcheckout時の改行規則だけの変更であり、taxonomy 58件、HMD、Generator、concept、datatype、dimension又はlinkbaseは変更していない。
- Formal GIT、stage、commit、push及びGitHub公開は実施していない。証跡はUADC_PoC `docs/ChatGPT/2026/202609/20260911/20260911_0850/taxonomy-publication-layout-canonical-resolution/outputs/`にある。

## 2026-09-11 XML/XSD LF publication baseline

- XBRL_GL_Next accepted base `fe1d9573f86267218dff152ad2e70a4600161e99` was fast-forwarded to `f30297a6148f32ce01a552f0dc3a7eb937f32fc9` on `origin/main`.
- The commit updates only `.gitattributes`, preserving the existing `*.csv -text` rule and adding `*.xsd text eol=lf` and `*.xml text eol=lf`.
- The 58 accepted Accounting Entries split-taxonomy Git blobs were already present and remain KEEP resources under `taxonomy/accounting-entries`; the legacy flat tree was not overwritten.
- Fresh-worktree Arelle 2.37.77 validation passed the Tuple and OIM entrypoints and the 12 dependent UADC monthly metadata files with exit 0, errors 0, warnings 0.
- Evidence is stored in UADC_PoC `docs/Codex/2026/202609/20260911/20260911_0932/formal-git-publication/outputs/`.

## 2026-09-15 legacy flat taxonomy WORK registration

- Official GIT promotion record `20260821_1249` identified accepted WORK `outputs/generated/run-a` as the source of commit `aa16412299b7064096cbc0935934c4cad18a4096` taxonomy bytes.
- The accepted old-namespace 76-file set was restored to canonical WORK path `taxonomy/`: REPLACE 55, KEEP 21, ADD 0; post-copy SHA matched 76/76.
- The later split successors under `taxonomy/accounting-entries` and `taxonomy/business-transactions` remain unchanged and retain their separate experimental-namespace lifecycle.
- Existing `taxonomy/TAXONOMY_MANIFEST.csv` describes a later 67-file set and is not the manifest for this restored family; 55 rows no longer match and remain `HOLD_USER_DECISION`.
- Validation was reused from the exact accepted execution set: A/B 76/76, package failures 0, Arelle four entrypoints error 0/warning 0. No duplicate test, Formal GIT, commit, or push was performed.

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

## 2026-09-17 XBRL Japan namespace-only Canonical WORK baseline

- Canonical taxonomy is limited to `taxonomy/accounting-entries/` (58 accepted files) and `taxonomy/business-transactions/` (67 accepted files), using `https://www.xbrl.or.jp/taxonomy/xbrl-gl-next/{module}`.
- The superseded parallel `xBRL-GL2.0_btx/` family (58 files) was removed after exact-byte backup and dependency-closure review.
- Post-migration accepted-family SHA continuity is 125/125; local relative references resolve 7999/7999; standard XBRL/W3C namespace references remain present.
- UADC_PoC dependent taxonomy alignment remains 22/22 exact-byte PASS. No UADC taxonomy file was changed.
- Existing taxonomy generation and Arelle PASS evidence was reused by SHA-256 identity; duplicate tests were not repeated.
- Evidence: `docs/Codex/2026/202609/20260917/20260917_132324/xbrl-japan-namespace-migration/outputs/`.
- Formal GIT, commit, push, and external publication were not performed.
