# XBRL-GL-Next Decisions

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
