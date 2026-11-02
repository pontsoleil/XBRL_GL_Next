[English](README.md) | **日本語**

# XBRL GL Next — Tavi概念実証

Tavi PWD 2026-09-01に基づく議論用試作です。正式なTavi適合性は確認されていません。

## Journal Entry PoC — 現行レビュー用ファイル

3-CubeのJournal Entryを、出現識別子が整数の版とUUIDv7の版で示します。いずれもレビュー用候補であり、正式なSemantic Model、HMD、Part 5を改訂するものではありません。

| 版 | Tavi Taxonomy | Instanceモジュール | Structured Tidy Data CSV |
| --- | --- | --- | --- |
| 整数型出現識別子 | [`tavi-tax.json`](taxonomy/tavi-tax.json) | [`tavi-ins.json`](instance/tavi-ins.json) | [`tavi-ins.csv`](instance/tavi-ins.csv) |
| UUIDv7型出現識別子 | [`tavi-uuid-tax.json`](taxonomy/tavi-uuid-tax.json) | [`tavi-uuid-ins.json`](instance/tavi-uuid-ins.json) | [`tavi-uuid-ins.csv`](instance/tavi-uuid-ins.csv) |

各Taxonomyは18列のTable Templateを`xbrlModel.tableTemplates`に含み、各CSVは18列・7出現レコードです。

各Instanceモジュールは、`documentInfo.importMapping`、`xbrlModel.importedTaxonomies`、`factMaps`、`factSources`、`documentInfo.sourceMappings`によってTaxonomyとCSVの対応を記述しています。ローカル参照の構造整合は確認済みですが、Taviネイティブ処理によるimport解決やFact再現は**未検証**です。レビュー用モジュールを正式適合のTaviインスタンスとして説明しません。

独立した[`tavi-schema.json`](taxonomy/tavi-schema.json)は、レビュー時に用いる外部JSON Schemaです。検証対象のTavi JSONには検証用の`$schema`や`$ref`を埋め込まず、スキーマを外部から指定します。このSchemaがXBRL Internationalの公式Schemaであることは確認されていません。

## Tavi Viewer

**[共通Tavi Viewer（HTMLソース）](viewer/tavi-viewer.html)** · [JavaScript](viewer/tavi-viewer.js)

共通Viewerは上記の通常版・UUID版の両方に対応します。上部でInstance JSONを選ぶと、左側の**Properties**にTable Template・Tavi Taxonomy・JSON Schemaの3タブを表示し、右側に**Structured Tidy Data CSVの転置表**を表示します。

現行Viewerは、`tavi-viewer.js`内の明示的な`KNOWN`一覧によってInstance・Taxonomy・CSVの対応を選びます。Instance JSONは読み込みますが、その`importMapping`や`sourceMappings`から対応ファイルを自動的に決定する実装では**ありません**。GitHubのファイル一覧で追加のJSONが表示されても、対応関係が承認されたことにはなりません。

### ローカルでの表示

`file://`でHTMLを直接開くのではなく、`tavi-poc/`をHTTP経由で表示してください。例えば、その親ディレクトリで以下を実行します。

```shell
python -m http.server 8765 --bind 127.0.0.1
```

ブラウザーで`http://127.0.0.1:8765/tavi-poc/viewer/tavi-viewer.html`を開きます。`tavi-viewer.html`と`tavi-viewer.js`を同じフォルダーに置き、`taxonomy/`と`instance/`をリポジトリ内の相対位置に保ってください。

**GitHub Pagesの状態：** 新しい共通ViewerのファイルはGitHubリポジトリに登録済みですが、**現時点ではGitHub Pagesに配信されていません**。既存のPagesワークフローは旧[Journal Entry静的Viewer](https://pontsoleil.github.io/XBRL_GL_Next/tavi-inst-hmd-view.html)だけを配信します。上記のHTMLへのリンクは、公開Viewerの動作URLではなくソースファイルへのリンクです。

Viewerはソース表示とCSVの静的閲覧用です。JSON Schema検証器、Taviネイティブ処理系、意味的適合性検証器ではありません。

## 履歴資料と検証範囲

旧Simple版、Full v3版、4モデルのTaxonomy、Arelleパッチ、旧レポートメタデータ経路は現行公開PoCの対象から撤回されています。原本と既存の履歴証跡はWORKに保全します。履歴資料や残存ファイルを現行サポート対象のInstance形式として説明しません。

2026年11月2日のレビュー用公開では、9ファイルの登録集合（新規7件・既存保持2件）についてCanonical登録、Official GIT反映、commit、pushが完了し、Pagesワークフローは変更していません。JSON構文、外部Draft-07による構造検証、CSVとTable Templateの整合、ローカル参照、Windows ChromeでのViewer表示を確認しました。これらの確認は、Tavi PWD正式適合、ネイティブimport意味解決、親出現識別の整合、Fact再現を証明するものではありません。
