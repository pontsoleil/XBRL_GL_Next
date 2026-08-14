# XBRL-GL-Next Handoff

更新日: 2026-08-14 (JST)

## 前回作業の結果

- WORK側の `semantic-model/` 10ファイルと `taxonomy/` 78ファイルをGIT側の同一相対パスへ同期した。
- 追加22、更新55、同一11で、WORK/GIT間のSHA-256は全88ファイル一致した。
- taxonomyの正式モジュール集合へ `ehm` と `muc` を反映し、HMD別module import集合からpackage checkerの期待値を導出するよう更新した。
- pytest 70件、62 subtests、taxonomy package checker、Arelleによるtaxonomy 4件・instance 4件の検証を完了した。
- 本書と同一commitを最新正式baselineとし、commit IDは `git rev-parse HEAD` で確認する。

## 現在の注意事項

- candidate LHMはGraph Walk生成物であり、手修正しない。
- reviewed LHMでは確定済み`semantic_path`をPost-Graph Walkが修復・再生成しない。
- XPathは`module`とreviewed `local_name`から生成し、`semantic_path`から独立させる。
- 正式moduleは `btx`、`bus`、`cor`、`ehm`、`lnk`、`muc`、`taf` の7件である。
- 対象外のWORK/GITファイルを一括同期しない。

## 次の作業

1. XBRL-GL-Next、UADC_PoC、LedgerExplorerのintegration manifestを定義する。
2. 正式HMD 2件とmanifestのcommit／SHA-256をUADC_PoC入力契約として固定する。
3. UADCのBinding Tableがcanonical `semantic_path`を全件解決することを確認する。
4. UADC出力Structured CSVをLedgerExplorerのdocument／journal／settlement viewへ接続する。
5. 3プロジェクトの入力、出力、件数、SHA-256、実行コマンド、期待結果を統合検証記録へ残す。

## 未完了・未確認

- XMLSpy GUIは今回再実行していない。
