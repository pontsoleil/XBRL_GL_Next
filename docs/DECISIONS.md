# XBRL-GL-Next Decisions

## 2026-08-30 Phase 1 canonical publication paths

- Use DTS-specific LHM and HMD directories under `semantic-model/LHM/{accounting-entries,business-transactions}/` and `semantic-model/HMD/{accounting-entries,business-transactions}/`.
- Keep the accepted static `gl-gen` seed under `tools/taxonomy/gen/`, distinct from generated DTS and legacy single-tree output.
- Store publication provenance outside generated DTS roots under `taxonomy/provenance/{accounting-entries,business-transactions}/`; reference canonical semantic inputs rather than duplicating them.
- Use `documents/taxonomy/README.md` for maintained split-taxonomy publication documentation. Keep `docs/**` as WORK-only evidence.
- Exclude `ids/**` and legacy single-tree cleanup from Phase 1.
- These decisions establish Canonical WORK paths but do not authorize Formal GIT or GitHub publication.

更新日: 2026-08-14 (JST)

## 採用済み設計指針

### D-001 semantic modelとbindingを分離する

- FSM、BSM、LHM、HMDはsemantic modelとtaxonomy生成の契約を表す。
- UADC固有Binding Table仕様をTaxonomy Framework Part 1へ混在させない。

### D-002 candidateからreviewedへの遷移は人手review境界とする

- candidate LHMを自動的にreviewedへ変更しない。
- reviewedの`local_name`と許容された`multiplicity`変更を設計者判断として保持する。

### D-003 source_bsm_idはprovenanceとする

- 同一`source_bsm_id`が複数の`semantic_path`へ展開されることを許容する。
- QName同一性やtaxonomy element再利用を`source_bsm_id`だけで決定しない。

### D-004 semantic_pathをcanonical化する

- termはASCII英字以外を除去する。
- Association roleとassociated Classは直接連結する。
- 空segment、正規化衝突、重複pathをerrorとし、Post-Graph Walkで修復しない。

### D-005 XPath生成をsemantic_pathから分離する

- XPathは階層ごとの`module`と確定済み`local_name`から生成する。
- reviewed入力に残る旧XPathを正本としない。

### D-006 TupleとOIMのDTSを分離する

- TupleはHMD別content schemaでstructural complexTypeを構成する。
- OIMはTuple content schemaへ依存せず、dimensional structureを使用する。
- 生成taxonomyはHMD、manifest、generatorから決定的に再生成できるようにする。

### D-007 連携境界を明示する

- UADC_PoCへ渡す正本は正式HMD 2件とmanifestである。
- LedgerExplorerへの表示入力はUADCが生成・検証したStructured CSVとする。
- 3プロジェクト間でファイルを暗黙共有せず、commit、相対パス、SHA-256、契約版を記録する。

## 保留事項

- 3プロジェクト共通integration manifestのschemaと配置先。
- WORK taxonomy追加2件及びWORK README／inventory差分の扱い。

### D-008 Account Identifier belongs to Accounting Entry Detail

- The abstract `cor:Detail` must not define an Account Identifier association.
- `cor:Entry_ Detail` explicitly composes `cor:Detail_ Account Identifier` with multiplicity `0..*`.
- `btx:Transaction_ Detail` must not expose Account Identifier because Business Transactions messages intentionally contain no ledger account codes.
- A concrete Detail specialisation must be selected explicitly where an abstract Detail association is intended to be expanded.
- All other abstract-target compositions formerly owned by `cor:Detail` are expressed against concrete `Detail_ ...` classes on `cor:Entry_ Detail` and `btx:Transaction_ Detail`.
- The abstract `Detail -> Detail` reference is removed and is not replaced with a recursive concrete self-reference because that would reuse one QName as both Class and Reference.

## 採用済み運用統制（2026-08-16）

### D-009 4プロジェクトで共通実行統制を固定する

- 決定日: 2026-08-16
- WORK共通 `AGENTS.md` を基準とし、4個別 `AGENTS.md` の第4章を同一章立て・同一記述にする。後続の固有章は共通基準を追加・強化するものであり、緩和しない。
- 読取り、編集、生成、copy、移動、名称変更、削除、GIT反映、Git操作、外部接続及び本番操作を別の承認区分とする。
- WORK側既存fileは実対象の個別指定なしに削除せず、mirror又は無指定再帰copyを禁止する。
- 非Git管理file等の変更前backup、失敗時の証跡と停止、決定的処理の再現性記録及び明示的な受入判定を必須統制とする。
- プロジェクト固有のdata保護、model/binding/Web/Apache/EC2/test及び成果物規則は維持する。

### D-010 テスト実行記録を必須成果物とする

- 決定日: 2026-08-16
- テストを1件以上実施した変更作業では、所定task記録の `outputs/TEST_RESULTS.md` を必須成果物とする。
- chat、console出力又は最終回答だけを正式記録の代替としない。
- test単位の結果、再実行に必要な環境・入力・設定・command、失敗・skip・warning、再現性、残存risk及び受入判定を記録する。
- テストを実施しなかった場合はfile作成を強制せず、未実施理由と影響を完了報告又は `HANDOFF.md` に記録する。

### D-011 Taxonomy GeneratorのHMD入力・出力場所を正式CLI化する

- 決定日: 2026-08-19
- XBRL GL Nextの `tools/taxonomy/xBRLGL_TaxonomyGenerator.py` を、Taxonomy family間で共用する唯一のGenerator本体とする。
- 既存の `--namespace` 契約は変更せず、HMD入力とTaxonomy出力の場所を `--hmd-dir` と `--output-dir` で正式に外部指定可能にする。
- 既存の位置引数 `lhm_for_taxonomy` と `-b` / `--base-dir` は後方互換として当面維持する。
- 旧指定と新指定を同時に使用した場合、正規化後の値が同じなら受理し、異なる場合は曖昧な優先順位を設けず明示エラーにする。
- 他Taxonomy familyへの適用は、同じXBRL GL Next HMDとnamespaceによる旧CLI／新CLIの生成物完全一致、再現性、既存テスト、package検証、全正式entry pointのArelle検証がPASSした後に限る。

### D-012 HMD module identityとXPath lexical namespace prefixを分離する

- 決定日: 2026-08-20
- 履歴状態: namespace URIに関する下記の旧規則は、2026-09-15のStable module namespace決定および2026-09-17のD-023により廃止された。module identityとlexical prefixを分離する原則だけを維持する。
- Canonical HMDの`module`をTaxonomy module identityとし、XPathで使用するlexical namespace prefixから独立させる。
- 共通Generatorは反復可能な`--namespace-prefix-map PREFIX=MODULE`で明示対応を受け付ける。family固有分岐又はprefixからfamilyを推測する処理を追加しない。
- mapping未指定の既存`gl-<module>`は従来どおり暗黙解決し、XBRL GL NextのCLI、QName、namespace、生成物を維持する。既存`gl-<module>`を別moduleへ再対応付けする指定は拒否する。
- namespace URIは引き続き`http://www.xbrl.org/int/gl/{module}/{version}`で生成し、lexical prefixの選択で変更しない。

### D-013 semantic datatypeとXBRL datatype bindingを外部定義で分離する

- 決定日: 2026-08-20
- Canonical HMDの`datatype`はsemantic representation termとして保持し、XBRL item typeは`definitions/taxonomy/datatype_mapping.csv`と必要最小限の`datatype_override.csv`によるbindingで決定する。
- lookup順序はexplicit override、default mapping、errorとする。未知のsemantic datatypeはerrorとし、string fallback及び`name`、`local_name`、生成type名のsuffixからの推測を行わない。
- `review-required`のmapping又はoverrideはformal generationで受理しない。`legacy-observed`は互換性の出典を記録するstatusであり、normative common defaultとみなさない。
- Generatorはfamily名による分岐を持たず、CLI指定がない場合は上記Canonical resourceを決定的に読む。HMDのsemantic field、namespace URI生成、`gl-gen`定義及びTaxonomy構築logicは変更しない。

### D-014 EN CIUS BT-125をbase64Binaryへbindingする

- 決定日: 2026-08-20
- CEN/TS 16931-3-2の区別に従い、BT-124 External document locationは`ExternalReference/cbc:URI`、BT-125 Attached documentは`Attachment/cbc:EmbeddedDocumentBinaryObject`として扱う。BT-125-1 `mimeCode`及びBT-125-2 `filename`は埋込みBinary Objectの属性である。
- semantic HMD datatype `Binary object`は変更せず、共通external mappingを`xs:base64Binary`／`xbrli:base64BinaryItemType`／unitなし／`confirmed`とする。
- 旧EN Taxonomyのstring fallbackはnormative precedentとせず、意図したbinding改善として扱う。

### D-015 Framework Parts 1–3 candidates become canonical WORK and formal GIT documents

- Decision date: 2026-08-21.
- The reviewed 2026-08-21 Part 1 and Part 2 candidates and the corrected Part 3 v3 candidate are adopted as the canonical WORK Taxonomy Framework Parts 1–3.
- Canonical identity is fixed by SHA-256: Part 1 `AB28B17FB1560F3A1008ACB27318F39B71CCCA5D182595992C458494DE147D9B`; Part 2 `5974DEF99D1418CFE9572573FF996400A04BADE81673B1FB792C117878E1CC95`; Part 3 `251BA08D929959665CFD23808084E1E5C74B5318F1D6B9A53F4ADA7D9E32514D`.
- The same files are the formal GIT/GitHub `main` documents from commit `fb09ff6f7cbd161a2c0c61a076e96e21973ce010`.
- This promotion does not modify the 18-column HMD/LHM contract, Generator, taxonomy, Tuple/OIM implementation, Value Domain implementation boundary, or ToC fields.

### D-016 Reviewed LHM is rebuilt from the latest candidate with a local-name-only overlay

- Decision date: 2026-08-24.
- For each taxonomy root, the complete latest candidate LHM is the authoritative structural and semantic base for the reviewed LHM.
- A prior reviewed LHM may contribute only its reviewed `local_name`, matched by stable semantic identity. `module`, `associated_module`, `semantic_path`, `xpath`, multiplicity, datatype, labels, definitions, and every other field remain from the latest candidate.
- A missing prior match preserves the candidate `local_name`; an ambiguous prior match is an error. The resulting reviewed LHM must contain every candidate row, differ from the candidate only in `local_name`, and have no duplicate `(module, local_name)` identity.
- The accepted processing order is latest candidate LHM plus prior reviewed `local_name` only, followed by official `post_graphwalk`, HMD for taxonomy, and the unchanged official Taxonomy Generator.
- The 2026-08-24 Business Transactions candidate verified this rule on 477 rows. This decision records the review reconstruction rule; it does not promote the candidate LHM, HMD, taxonomy, or Binding to production or formal GIT.

### D-017 Accounting Entries and Business Transactions use separate canonical DTS roots

- Decision date: 2026-08-30.
- The Canonical WORK taxonomy authority is split by HMD scope: Accounting Entries is `taxonomy/accounting-entries/`; Business Transactions is `taxonomy/business-transactions/`.
- Each root contains one complete accepted successor-A DTS with its internal relative paths and bytes preserved. Shared-looking files are not merged, deduplicated, or referenced across the two roots.
- The former single-tree taxonomy is not authority for these split DTS roots. It remains unchanged pending a separately authorized cleanup decision.
- This decision authorizes Canonical WORK placement only; it does not authorize Formal GIT or GitHub publication.

### D-018 datatype_binding.pyのMIT表記をCanonical WORKへ採用する

- 決定日: 2026-09-11
- 現行`AGENTS.md`の明示指定、既存project-authored toolのSPDX headers、受入済みsuccessor `LICENSE.md`及び同一内容のheader付き`datatype_binding.py`を来歴根拠とする。
- 変更はshebang直後の`SPDX-License-Identifier: MIT`追加だけで、AST及び実行機能は同一とする。
- この採用はrepository全資源のlicense変更、taxonomy artefactの公開許可又はFormal GIT昇格を意味しない。

### D-019 taxonomy XML/XSDのCanonical改行をLFへ固定する

- 決定日: 2026-09-11
- accepted `TAXONOMY_MANIFEST.csv`が記録するfilesystem SHA-256をOS及び`core.autocrlf`設定に依存させないため、`.gitattributes`で`*.xsd text eol=lf`及び`*.xml text eol=lf`を定める。
- この変更はGit checkout規則であり、生成済みtaxonomy、HMD、Generator又は意味モデルの機能変更ではない。
- task-local cloneで`core.autocrlf=true`でもOIM entrypoint SHAが一致することを受入条件とし、検証PASSを確認した。
- Canonical WORKへの追加だけを承認範囲とし、Formal GIT又はGitHubへの反映は別承認とする。

### D-020 Official GITへ昇格済みの旧namespace一式をWORK正規位置へ復元する

- 決定日: 2026-09-15。
- Official GIT commit `aa16412299b7064096cbc0935934c4cad18a4096`へのコピー記録が示す受入済みWORK `20260821_1249/.../outputs/generated/run-a`をコピー元権威とする。
- 旧`http://www.xbrl.org/int/gl/.../2026-12-31`の76ファイル一式を`taxonomy/`へexact-byte登録し、部分的なnamespace混在を解消する。
- 新`xbrl.or.jp/.../experimental/...`の分割正本2ツリーは別の後続release familyとして維持し、今回変更しない。
- 本決定はWORK登録に限り、Formal GIT、GitHub、公開又は暫定namespaceの公式性を承認しない。

### D-021 9月4日税取引分類追加版へTax Typeを併存させた後継版をCanonical WORKへ採用する

- 決定日: 2026-09-15。
- `cor:taxTransactionClassification`はPurchase／Salesを表し、`cor:taxType`はVAT／OTHを表す。`OTH`は消費税以外の法人税等のための値であり、両conceptを置換せず併存させる。
- Accounting Entries HMDは400行、SHA-256 `CE7FDCB8013CCDB2CF2513107F972F174ACC0BBA5207EEB12DE206DC0B08F500`を採用し、日付local nameは`entryDatePosted`とする。
- A/B 58/58決定性、package failures 0、Tuple/OIM Arelle error 0／warning 0及びUADC PCA／EPSON正式xBRL-CSV error 0／warning 0を受入根拠とする。
- 検証済みexact bytesを`taxonomy/accounting-entries/`とAccounting Entries HMD 2配置へ登録する。Formal GIT、GitHub及び公開は別承認とする。
- 根拠: `docs/Codex/2026/202609/20260915/20260915_1101/adopt-20260904-tax-classification-baseline/outputs/successor-tax-type/`。

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

### D-023 XBRL Japan namespace taxonomyへ一本化する

- 決定日: 2026-09-17。
- Canonical WORKの現行taxonomyは`taxonomy/accounting-entries/`（58 files）および`taxonomy/business-transactions/`（67 files）だけとし、project module namespace authorityを`https://www.xbrl.or.jp/taxonomy/xbrl-gl-next/{module}`へ一本化する。
- 旧XBRL International domainを使う並行family `xBRL-GL2.0_btx/` 58 filesは、受入済みXBRL Japan familyとdependency closureを確認し、全bytesをtask-local backupへ保存した後に削除した。
- XBRL 2.1、XBRL Dimensions、XLink、XMLおよびXML Schemaの標準namespaceは変更しない。
- 旧namespaceを記すD-012およびD-020はmigration historyとして保持するが、現行authorityには使用しない。
- 受入済みtaxonomy 125/125のSHA-256 identity、relative reference 7999/7999、UADC dependent copy 22/22を確認した。既存Arelleおよび生成試験は再実行していない。
- 根拠: `docs/Codex/2026/202609/20260917/20260917_132324/xbrl-japan-namespace-migration/outputs/`。Formal GITおよびGitHub操作は別ゲートとする。
