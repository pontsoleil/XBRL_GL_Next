# XBRL-GL-Next Current Baseline

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
