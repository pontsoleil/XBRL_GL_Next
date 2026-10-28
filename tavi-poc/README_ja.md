[English](README.md) | **日本語**

# XBRL GL Next — Tavi概念実証

Tavi公開作業草案を基礎として、XBRL GL Nextの意味定義をJSONタクソノミとして表現する概念実証です。4種類の独立したHMD由来タクソノミ、学習用・ビュー用の例、Arelle OimTaxonomy拡張を公開しています。関係者との共同技術検討を目的とするプロジェクト公開であり、標準化団体による正式endorsementやTavi仕様への全面適合を主張するものではありません。


`taxonomy/`は、`semantic-model/HMD/`にあるモデル別の正式HMDを共通の意味的入力として、XBRL 2.1 Tuple、OIM、Taviの3種類のタクソノミを公開する領域です。各モデルに対応する3形式はそのモデルの正式HMDに基づきます。ただし、過去の各生成実行でHMDの同一ファイル版を使用したことまで、この案内だけで保証しません。共通ViewシートからTuple XML、OIM CSV＋JSONメタデータ、Tavi CSV＋JSONメタデータの3種類のインスタンスを生成する統一工程は、次の開発段階です。

`tavi-poc/`は、Taviのタクソノミとインスタンスを独立に試作・評価する環境です。`taxonomy/`で使用する正式HMDや生成工程を共有するものではありません。Simple、Full v3、HMD View等の試作例は、`taxonomy/tavi/`の4モデルと同一の成果物ではありません。

## HMD由来の4モデル

| モデル | ルート | 公開タクソノミ |
| --- | --- | --- |
| COR | `cor:accountingEntries` | [Accounting Entries](../taxonomy/tavi/accounting-entries/taxonomy.json) |
| COR-JPN | `jpn:accountingEntries` | [Accounting Entries — Japan](../taxonomy/tavi/accounting-entries-jpn/taxonomy.json) |
| BTX | `btx:businessTransactions` | [Business Transactions](../taxonomy/tavi/business-transactions/taxonomy.json) |
| BTX-PINT | `pint:businessTransactions` | [Business Transactions — PINT](../taxonomy/tavi/business-transactions-pint/taxonomy.json) |

モデルごとに独立した18列の正式HMDを使用します。[HMDからTaviへの生成器](tools/hmd_to_tavi.py)はHMDを1件ずつ読み取り、タクソノミを生成します。Specialisation、Graph Walk、インスタンス生成は行いません。[4モデル再現手順（英語）](README_REPRODUCE_4_MODELS.md)と[4モデル概要（英語）](README_ADDENDUM_4_MODELS.md)を参照してください。

## その他の公開例

| 例 | タクソノミ | レポート・ビュー |
| --- | --- | --- |
| Simple Tavi | [最小タクソノミ](taxonomy/tavi-tax.json) | [JSONメタデータ](instance/tavi-inst.json)＋[CSV](instance/tavi-inst.csv) |
| Full Accounting Entries v3 | [Full v3タクソノミ](taxonomy/XBRL_GL_Next_Tavi_AccountingEntries_v3.json) | タクソノミのみ。対応するFullインスタンス一式の公開は主張しません |
| Single Account Date r2 HMD View | [ビュー用タクソノミ](profiles/single-account-date-r2/taxonomy/Tavi_JournalEntries_SingleAccount_Date_r2_candidate.json) | [ビュー用メタデータ](instance/tavi-inst-hmd-view.json)、[プロファイル用メタデータ](profiles/single-account-date-r2/instance/tavi-inst-nine-column-Date-r2-candidate.json)と参照CSV |

インスタンスをArelleで開くときは、対応するJSONメタデータを入口にします。CSV単独では完全なxBRL-CSVレポートになりません。Simple、Full v3、HMD View、4モデルのタクソノミは適用範囲が異なり、相互に交換できません。

## Arelleと静的Viewer

[Arelleパッチ適用手順（英語）](arelle/APPLY_PATCH.md)および[環境手順（英語）](arelle/ENVIRONMENT.md)に、独立したArelleチェックアウトでOimTaxonomyを利用する方法を示します。PoCで扱うのは、記載されたパッチ範囲でのタクソノミ読込み、native fact表示、Structured Tidy Data転置表示、ラベル言語選択です。

- [Simple Tavi Viewer](https://pontsoleil.github.io/XBRL_GL_Next/tavi-inst.html)
- [HMD View Viewer](https://pontsoleil.github.io/XBRL_GL_Next/tavi-inst-hmd-view.html)

これらは静的表示であり、正式なTavi検証器ではありません。4モデルの受入結果はタクソノミ生成・native DTS読込みに関するものです。一般的なView→Taviインスタンス自動生成や4モデルのインスタンス検証が完了したことを示しません。
