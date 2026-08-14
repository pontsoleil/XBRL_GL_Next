# XBRL-GL-Next Handoff

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
