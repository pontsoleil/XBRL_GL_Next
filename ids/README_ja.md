[English](README.md) | **日本語**

# XBRL GL Next サンプルインスタンス

このディレクトリには、XBRL GL Next の2つのサンプル HMD に対応する小規模なインスタンス例を格納しています。

- `cor_accountingEntries`
- `btx_businessTransactions`

同じレビュー済みセマンティックモデルを Tuple binding と OIM binding のそれぞれでどのように報告できるかを示す informative な例です。これらのサンプルが Framework に追加の要求事項を定義するものではありません。

## 内容

```text
ids/
├─ README.md
├─ README_ja.md
├─ VALIDATION_REPORT.md
├─ tuple/
│  ├─ accountingEntries-journalEntry.xml
│  └─ businessTransactions-vendorInvoice.xml
└─ oim/
   ├─ accountingEntries-journalEntry.json
   ├─ accountingEntries-journalEntry.csv
   ├─ businessTransactions-vendorInvoice.json
   └─ businessTransactions-vendorInvoice.csv
```

## Tuple サンプル

Tuple サンプルは XBRL 2.1 XML インスタンスです。

- `tuple/accountingEntries-journalEntry.xml`
- `tuple/businessTransactions-vendorInvoice.xml`

XML ファイルをインスタンス文書として開きます。インスタンスは `../taxonomy/tuple/` 配下の対応する Tuple タクソノミ entry point を参照します。

これらの例は、formal HMD から生成された物理的な Tuple 階層を示します。

## OIM / xBRL-CSV サンプル

各 OIM サンプルは、同じ basename を持つ2ファイルから構成されます。

- JSON metadata file
- 1つの Structured CSV data file

例:

```text
oim/accountingEntries-journalEntry.json
oim/accountingEntries-journalEntry.csv
```

**JSON ファイルが report entry point です。** Arelle で xBRL-CSV サンプルを開く場合は、`.csv` ではなく `.json` を開いてください。

CSV は1つの矩形 Structured CSV table のままです。Class occurrence は typed dimension に対応する occurrence-key column で識別され、Class ごとの正規化テーブルには分割しません。

## サンプルの使い方

このディレクトリ配下のサンプルインスタンスを開きます。

1. Tuple は `tuple/` 配下の対応する XML インスタンスを開きます。
2. OIM/xBRL-CSV は `oim/` 配下の対応する JSON metadata file を開きます。JSON ファイルが report entry point であり、対応する CSV はその metadata を通じて読み込まれます。
3. インスタンスまたは OIM metadata が `../taxonomy/` 配下の対応する taxonomy entry point を参照し、XBRL processor がそれを discover します。
4. report facts を taxonomy presentation と併せて確認し、OIM では dimensional network も確認します。
5. Taxonomy Framework Parts 2 and 3 で定義する binding の informative な実例として使用します。

## 検証

インスタンス検証記録は [`VALIDATION_REPORT.md`](VALIDATION_REPORT.md) を参照してください。

2026-08-12 の受入 baseline は Arelle 2.44.1 で次のとおり検証済みです。

- Tuple instances: 2/2、error 0 / warning 0
- OIM instances: 2/2、error 0 / warning 0

## 編集方針

これらは登録済みサンプルタクソノミに対応するサンプルインスタンスです。formal taxonomy を変更した場合は、必要なサンプル変更を明示的に行い、検証を再実行してください。taxonomy や semantic-model の問題を隠すためだけにインスタンスを変更してはいけません。
