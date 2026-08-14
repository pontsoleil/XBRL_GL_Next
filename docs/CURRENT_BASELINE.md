# XBRL-GL-Next Current Baseline

記録日: 2026-08-14 (JST)

## Git baseline

- branch: `main`
- upstream: `origin/main`
- pre-sync baseline commit: `479d50fba73800c53e4439708f407b5de4b3eb24`
- pre-sync subject: `Add project baseline and handoff records`
- 記録時点のahead/behind: `0/0`
- 本更新を含むcommitは自己参照を避けるため固定値として記録しない。最新値は`git rev-parse HEAD`で確認する。

## 正式入力

|相対パス|用途|SHA-256|
|---|---|---|
|`semantic-model/LHM/LHM_candidate.csv`|Graph Walk candidate LHM|`FF153C83629A4AE81EED2DCBFE97E6B95C6C9526013F505ADECF7808E3A9EDFA`|
|`semantic-model/LHM/XBRL_GL_Next_LHM_reviewed.csv`|設計者reviewed LHM|`ED7FCB39664C76299BAF29F923B1CE1615658264AB02F29E8198A3154D534BEF`|
|`semantic-model/LHM_for_taxonomy/XBRL_GL_Next_HMD_AccountingEntries_for_taxonomy.csv`|Accounting Entries HMD|`0730006AAA1F84C9E14F1347BF134F40A02A9F0B660A34849F465F57C8509E2A`|
|`semantic-model/LHM_for_taxonomy/XBRL_GL_Next_HMD_BusinessTransactions_for_taxonomy.csv`|Business Transactions HMD|`49D54DF6536E37C3911650535E33F55AC5F6FA6E3ED620D6AC355E8ED318BE01`|
|`semantic-model/LHM_for_taxonomy/manifest.csv`|正式HMD manifest|`9F940D302AFE041CFF3299258A6A28A0EF5077230546F8F554099CC7DC93C605`|

正式処理経路はFSM → Specialisation → BSM → Graph Walk → candidate LHM → human review → Post-Graph Walk → HMD → Taxonomy Generatorである。

## 正式成果物と実装

- taxonomy: 76生成ファイル
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

今回のWORK同期後の受入記録:

- Graph Walk／Post-Graph Walk／semantic pipelineを含むpytest 70件、62 subtests成功
- 正式FSMからtaxonomyまでの再生成内容・SHA-256一致
- taxonomy 76ファイル、local reference 6,011件、dimensional locator 1,437件
- repository checker failure 0、未解決file 0、未解決fragment 0
- Arelle 2.23.1: taxonomy entry point 4件及びinstance entry point 4件でerror 0、warning 0
- canonical `semantic_path`、18列契約、reviewed `local_name`／XPathを維持

## WORK差分

- WORKの `semantic-model/` 10ファイル及び `taxonomy/` 78ファイルは、GIT側の同一相対パスとSHA-256が全件一致する。
- 正式taxonomyはXML/XSD 76ファイルで構成し、`README.md`、`README_ja.md`は生成ファイル数に含めない。
- WORKの対象外ディレクトリは同期していない。
