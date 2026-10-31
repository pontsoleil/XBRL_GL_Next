[English](README.md) | **日本語**

# 公開タクソノミ

`taxonomy/`はモデル別の正式HMDに基づくTuple／OIMの独立タクソノミを収録します。Journal Entry Tavi議論用候補は`tavi-poc/`の別scopeです。共通Viewから3形式のインスタンスを生成する統一工程は今後の対象です。




このディレクトリには、独立したXBRL 2.1 Tuple／OIMタクソノミと、実験的なTavi JSONタクソノミを収録しています。

## Tuple／OIM

- [`accounting-entries/`](accounting-entries/) — Accounting Entries（COR）
- [`business-transactions/`](business-transactions/) — Business Transactions（BTX）
- [`journal-entries/`](journal-entries/) — 独立した仕訳モデル

用途とbindingに合うentry pointを選択してください。同名conceptがあることを理由に、独立生成されたDTSを無条件に統合しないでください。module namespaceは`https://www.xbrl.or.jp/taxonomy/xbrl-gl-next/{module}`形式であり、ファイル名の日付をnamespace URIに含めません。

## Tavi JSON

Tavi PWD 2026-09-01を参照した議論用試作。正式適合性は未確認。 唯一のTavi公開対象は[Journal Entry JSON](../tavi-poc/taxonomy/Tavi_JournalEntries_SingleAccount_Date_r2_candidate.json)です。Table Templateを内包します。[静的Viewer](https://pontsoleil.github.io/XBRL_GL_Next/tavi-inst-hmd-view.html)は正式な適合性検証器ではありません。

公開条件と出所については[第三者資料の注意事項](../THIRD_PARTY_NOTICES_ja.md)を参照してください。
