[English](README.md) | **日本語**
# XBRL GL Next インスタンス文書（ids）

**`ids`はXBRL Instance Documents（インスタンス文書）の略**です。識別子定義のディレクトリではありません。

- `tuple/`：XBRL 2.1のXMLインスタンス。XMLファイルが入口です。
- `oim/`：CSVと対応するJSONメタデータからなるxBRL-CSVレポート。**JSONメタデータが入口**で、CSVと不可分です。

対応する独立タクソノミは[`taxonomy/`](../taxonomy/)を参照してください。過去の検証結果は、今回の新規検証結果ではありません。

[`tavi-poc/instance/`](../tavi-poc/instance/)は別のPoCです。View定義からの汎用Taviインスタンス自動生成は未確認です。
