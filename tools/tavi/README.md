# Tavi Viewer HTML生成器

この文書は退役したローカルHTML Viewer生成処理の技術説明と受入履歴を保持します。生成器と実行用スクリプトは現行Canonicalには含まれず、以下は現行のインストール・実行手順ではありません。公開済み静的HTMLを表示することと、ローカルでHTMLを再生成することは別です。

## 目的・機能

Phase 1の静的Viewerを生成します。左側にTable TemplateとTavi taxonomyのJSON原文をCSSタブで表示し、右側にCSVの行列を転置して表示します。HTML内にデータとCSSを含め、JavaScriptや外部取得を必要としません。taxonomyの意味解析や正式XBRL/Tavi validation、fact選択によるProperties連動は行いません。

## 入力の関係

入口はxBRL-CSVのJSON metadataです。`documentInfo.taxonomy`の明示的なローカルJSON参照1件と、各`tables.<id>.url`のCSVをmetadataの親ディレクトリから解決します。`tables.<id>.template`が選ぶ`tableTemplates`内のobjectを原文のまま表示します。taxonomy/CSVを別引数で差し替えません。ネットワークURL、fragment、queryや未対応のextendsを拒否し、欠落参照を探索・補完しません。

## 実行環境・依存

生成器・実行用スクリプトはPython標準ライブラリのみを使います。既存受入環境はmacOS、Python 3.10.1です。Python 3.10系での受入証跡があり、別バージョンの全互換性を保証するものではありません。Arelle、BeautifulSoup、Puppeteerは生成runtimeの依存ではありません。これらを使った過去QAと生成runtimeを区別してください。

過去の実装では、実行用スクリプトが隣接する生成器を同じPythonで起動し、引数と終了コードを引き継ぎました。この構成は履歴上の説明であり、現行Canonicalへのスクリプト復元や実行を指示しません。

## 旧CLI契約（履歴）

- `--metadata PATH`：必須。入力JSON metadata。
- `--output PATH`：必須。新規HTMLの保存先。
- `--help`：既存生成器のヘルプ。

相対CLIパスは実行時のカレントディレクトリ基準です。taxonomy/CSVの相対参照はmetadata所在基準です。空白を含むパスは引用してください。

## 公開済み静的HTMLの参照

- [Simple Tavi Viewer](https://pontsoleil.github.io/XBRL_GL_Next/tavi-inst.html)
- [HMD View Viewer](https://pontsoleil.github.io/XBRL_GL_Next/tavi-inst-hmd-view.html)

上記は既存の静的表示です。ローカル生成スクリプトを実行する手順ではなく、正式なXBRL/Tavi検証を行うものでもありません。過去の入力例は`tavi-poc/instance/tavi-inst.json`と`tavi-poc/instance/tavi-inst-hmd-view.json`で、metadataからtaxonomy/CSVを相対参照する技術説明は上記および同階層の仕様書に保持します。HMD View metadataは登録されたprofile内taxonomyを参照するため、metadataだけを別配置へ移して参照を補完してはなりません。

## 出力・注意事項

出力は`.html`拡張子で指定します。生成器は親ディレクトリを必要に応じて作成しますが、既存出力ファイルは拒否します。公開Viewerを指定せず、WORK task内の未使用パスを指定してください。入力はUTF-8で、CSVは入力BOM許容です。出力HTMLはUTF-8です。入力ファイルを変更しません。

未対応・不正な入力や参照でHOLD表示と終了コード2を返します。正常終了は0です。CSVを数値/日付へ変換せず、列順、空欄、文字列を保持します。正式仕様の範囲を超えるテンプレートを独自に補完しません。

## 受入範囲・証跡

同階層の`TAVI_INSTANCE_HTML_GENERATOR_SPEC.md`は、この過去実装の入力・出力・表示契約を説明する仕様書として保持します。採用・実行・受入の原記録はWORKで保全されており、退役した登録記録やtask内ログを現行の実行入力として要求しません。

既存受入はSimple/HMDの2ケース、原文表示、CSV転置、CSSタブ、Chrome表示のPhase 1範囲です。20261015_1918/tavi-viewer-script-identityで現在公開HTMLとのraw SHA一致を確認しました。これらは過去の受入履歴であり、今回新しい実行を行ったという意味ではありません。過去試験を新スクリプトの実行実績とみなしません。

受入済み生成器SHA-256:
`b3032d8579493c68cbed67ba2345c3abdf03b5c0c6b6eb4383e84f7244ce7621`

## Windows 11

旧実装のWindowsでの動作確認は未実施です。MacBookでの受入範囲と、別OSでの実行成功を混同しません。この履歴説明はスクリプトの復元・再転送・依存版の整備・実行を指示するものではありません。
