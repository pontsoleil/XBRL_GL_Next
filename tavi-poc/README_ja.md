[English](README.md) | **日本語**

# XBRL GL Next Tavi PoC

本PoCは、HeaderとDetailの会計仕訳をTavi/OIMタクソノミとxBRL-CSVのメタデータ＋CSVレポートで表現します。3つのArelle OimTaxonomyパッチにより、native factの読込み、読み込まれたモデルから再構成するStructured Tidy Dataの転置表示、およびタクソノミ表示で選択したラベル言語への対応を提供します。

本パッケージは、指定したArelle baseへの新規インストールを対象とする初回公開候補です。実験的なものであり、仕様への完全適合、upstream Arelleのリリース、他のArelle版との一般的な互換性を主張するものではありません。

## 3種類のTaviタクソノミと2種類のレポート定義

Simple、COR Full、HMD Viewは目的が異なるタクソノミであり、相互に交換できるものではありません。ここでの区分は説明上の事例であり、実行時のprofile設定ではありません。

Table 1に、公開タクソノミとレポートの組合せを示します。

Table 1 — Taviタクソノミとレポートの提供状況

| 区分 | 公開済みタクソノミJSON | インスタンスCSV／JSONメタデータ | 静的HTML Viewer |
| --- | --- | --- | --- |
| Simple Tavi | [tavi-tax.json](taxonomy/tavi-tax.json) | 公開済みの[tavi-inst.json](instance/tavi-inst.json)と[tavi-inst.csv](instance/tavi-inst.csv) | [Simple Tavi Viewer](https://pontsoleil.github.io/XBRL_GL_Next/tavi-inst.html) |
| COR Full Accounting Entries | [XBRL_GL_Next_Tavi_AccountingEntries_v3.json](taxonomy/XBRL_GL_Next_Tavi_AccountingEntries_v3.json) | **なし** | **なし** |
| HMD View — Single Account Date r2 | [Tavi_JournalEntries_SingleAccount_Date_r2_candidate.json](profiles/single-account-date-r2/taxonomy/Tavi_JournalEntries_SingleAccount_Date_r2_candidate.json) | Canonical登録済みの`tavi-inst-hmd-view.json`とSimple Tavi共通のCSV。メタデータは**独立したGitHubファイルとしては未公開** | [HMD View Viewer](https://pontsoleil.github.io/XBRL_GL_Next/tavi-inst-hmd-view.html) |

Simple TaviはタクソノミとTable Templateの基本的な定義を示します。COR FullはCOR Accounting EntriesのFull HMD由来タクソノミを表し、HMD Viewは用途別に選択したビューを表します。

COR Fullは**タクソノミのみの成果物**です。対応するインスタンスCSV、インスタンスJSONメタデータ、HTML Viewerはありません。過去のデータ0行の`accountingEntriesV3` Table Template scaffoldとそのCSV／JSONはCanonical登録・公開対象外であり、本パッケージのFullインスタンスとして扱いません。

SimpleとHMD Viewは、同じStructured Tidy Data CSVを使う2種類のメタデータ／タクソノミの組合せです。異なるCSVデータセットが2つあるという意味ではありません。HMD ViewメタデータはCanonical登録済みであり、そのTable Templateとタクソノミのソースは公開済み静的Viewerで表示されます。ただし、それによってメタデータが独立したGitHub JSONファイルとして取得できることにはなりません。

公開済みHMD Viewタクソノミは受入済みCanonicalとバイト単位で一致します（SHA-256：`5c78270b3fb9e3ed57f5ffb3b97a2f7a5694d11f68728a57b650d5a73890c80e`）。ファイル名の`candidate`は従来の名称として保持されており、受入範囲は登録記録で判断します。

## PoCの実行（Run the PoC）

1. 公開base `0c773d6f79681caf598aded5ccb3812bbb0b9b28`の、別のクリーンなArelleチェックアウトを用意します。
2. 提供されたファイルのハッシュを確認し、次の順序でパッチを適用します。
   1. `arelle-oimtaxonomy-tavi-poc.patch`：受入済みloader、DTS、native xBRL-CSVおよび当初のStructured Tidy Data実装。
   2. `0010-oim-taxonomy-structured-tidy-transposed-view.patch`：Structured Tidy Dataの転置表示とItem／native factのProperties選択。
   3. `arelle-oimtaxonomy-label-language-additional.patch`：タクソノミ表示で選択したラベル言語への対応。
3. checkout、パッチ、Python/Tkの前提条件、ハッシュ、プラグイン設定の正確な手順は[APPLY_PATCH.md](arelle/APPLY_PATCH.md)に従ってください。
4. 新しいArelleチェックアウトからGUIを起動します。

   ```bash
   .venv/bin/python arelleGUI.pyw
   ```

   ガイドに従い、**Help → Manage plug-ins**から**OIM Taxonomy**を有効にします。
5. **File → Open**で、以下に示す各タクソノミを確認します。最小レポート例は、[instance/tavi-inst.json](instance/tavi-inst.json)を入口として開きます。

## パッケージ（Package）

- [taxonomy/tavi-tax.json](taxonomy/tavi-tax.json)：7 conceptsと2 cubesを持つ最小Header/Detailタクソノミです。提供する最小メタデータ／CSV例はこのタクソノミを使用します。
- [taxonomy/XBRL_GL_Next_Tavi_AccountingEntries_v3.json](taxonomy/XBRL_GL_Next_Tavi_AccountingEntries_v3.json)：Full HMD由来のAccounting Entriesタクソノミで、399 concepts、44 dimensions、45 domains、46 cubes、1 networkを持ちます。Groups定義とTable Templatesはありません。
- [instance/tavi-inst.json](instance/tavi-inst.json)と[instance/tavi-inst.csv](instance/tavi-inst.csv)：既存の最小レポート例です。メタデータJSONを開いてください。
- [パッチガイド](arelle/APPLY_PATCH.md)：3つのパッチすべてを新規インストールへ適用する手順です。
- 過去の整合性・受入記録はWORKに保持しており、実行入力ではありません。パッチ順序とsource hash条件は[パッチガイド](arelle/APPLY_PATCH.md)を参照してください。
- v3のdatatype来歴と保存済みFull DTS受入記録は、タクソノミ本体とは区別してWORKに保全しています。
- [当初の期待結果](expected/STRUCTURED_TIDY_DATA.md)は0010以前の歴史的な配置を示します。当初の9列配置は、最終的な転置配置とは異なります。累積パッチの過去受入記録はWORKに保持しています。

タクソノミ、インスタンス、パッチのバイト列は保持されています。最終的な最小レポート表示は、9つのItem行と6つの出現列を持ち、native fact／Propertiesへの対応があります。

## Tavi PoC — Structured Tidy Data Viewer

Tavi PoCでは、同じStructured Tidy Data CSVを、2種類のTaviタクソノミ定義で表示する方法を示します。

### オンラインViewer

- **[Simple Tavi Viewer](https://pontsoleil.github.io/XBRL_GL_Next/tavi-inst.html)** — Taviタクソノミ、Table Template、CSVインスタンスの関係を示す基本例です。
- **[HMD View Viewer](https://pontsoleil.github.io/XBRL_GL_Next/tavi-inst-hmd-view.html)** — XBRL GL NextのHMD Viewに基づき、同じCSVを異なるタクソノミ定義で表示する例です。

各Viewerは2つのパネルを提供します。

- **左側：** Table TemplateとTaviタクソノミのJSON原文をタブで切り替えて表示します。
- **右側：** Structured Tidy Data CSVを行列転置して表示します。

これらは過去に生成された静的HTMLです。旧ローカルHTML生成スクリプトは現行Canonicalには含まれず、本案内はその実行を要求しません。公開HTMLを表示することと、ローカル生成処理は別です。

**Phase 1**は、JavaScriptを使わない自己完結型の静的HTMLです。**Phase 2**では、Table Templateとタクソノミ定義に基づく対話的なProperties表示を導入する予定です。

これらのViewerはデモンストレーション用であり、正式なXBRL/Tavi validationを行いません。

Canonical登録、GitHub公開、静的HTML表示の受入、正式なXBRL/Tavi validationは別の状態です。Viewerによるソース表示は正式validationの証拠ではありません。B5検証問題は別課題として残ります。HTMLのPhase 2は未着手であり、前述のArelle native fact／Properties機能とは別の実装です。

## 開発baseline（Development baseline）

受入済み開発リポジトリでは、ブランチ`work/oim-taxonomy-tavi`と次のcommitを使用しました。

- 累積実装：`f8f50ee1d06a12f2e9798437c66e2d360514d6be`。
- 0010：`7fe66c11cda8f23d60149cb119e3646f4a508fe3`。
- ラベル対応／最終開発HEAD：`d19d2e7ad369f3356746252d1f63d808ed4281cc`。

配布パッチの適用により、記録されたソース内容とSHA-256を再現できます。これらのGit commit IDが作られるわけではありません。保存済みのnative／GUI受入記録を再利用しており、初回公開文書候補には静的照合のみを実施しています。

## macOS GUI操作（macOS GUI operation）

タブを操作する前に、Arelleウィンドウ内をクリックしてアクティブにしてください。ユーザーからは、Cubesタブを直接クリックした際にはGroupsが選択されたままだった一方、ウィンドウ内をクリックしてからCubesをクリックすると切り替わったとの観察がありました。実際にactivationとfocusのどちらが変わったか、およびTk/macOS runtime側の原因は未確認です。

v3にはGroups定義がないため、**XBRL Groups**が空であることは想定どおりです。**XBRL Networks**と**XBRL Cubes**を確認してください。最小タクソノミではNetworksは空で、Cubesには`cor:entryHeaderCube`と`cor:entryDetailCube`があるはずです。
