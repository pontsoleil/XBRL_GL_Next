[English](README.md) | **日本語**

# 公開タクソノミ

`taxonomy/`は、`semantic-model/HMD/`にあるモデル別の正式HMDを共通の意味的入力として、XBRL 2.1 Tuple、OIM、Taviの3種類のタクソノミを公開する領域です。各モデルに対応する3形式はそのモデルの正式HMDに基づきます。ただし、過去の各生成実行でHMDの同一ファイル版を使用したことまで、この案内だけで保証しません。共通ViewシートからTuple XML、OIM CSV＋JSONメタデータ、Tavi CSV＋JSONメタデータの3種類のインスタンスを生成する統一工程は、次の開発段階です。

`tavi-poc/`は、Taviのタクソノミとインスタンスを独立に試作・評価する環境です。`taxonomy/`で使用する正式HMDや生成工程を共有するものではありません。Simple、Full v3、HMD View等の試作例は、`taxonomy/tavi/`の4モデルと同一の成果物ではありません。


このディレクトリには、独立したXBRL 2.1 Tuple／OIMタクソノミと、実験的なTavi JSONタクソノミを収録しています。

## Tuple／OIM

- [`accounting-entries/`](accounting-entries/) — Accounting Entries（COR）
- [`business-transactions/`](business-transactions/) — Business Transactions（BTX）
- [`journal-entries/`](journal-entries/) — 独立した仕訳モデル

用途とbindingに合うentry pointを選択してください。同名conceptがあることを理由に、独立生成されたDTSを無条件に統合しないでください。module namespaceは`https://www.xbrl.or.jp/taxonomy/xbrl-gl-next/{module}`形式であり、ファイル名の日付をnamespace URIに含めません。

## Tavi JSON

[`tavi/`](tavi/)には、次の独立したtaxonomyを公開しています。

- [COR](tavi/accounting-entries/taxonomy.json)
- [COR-JPN](tavi/accounting-entries-jpn/taxonomy.json)
- [BTX](tavi/business-transactions/taxonomy.json)
- [BTX-PINT](tavi/business-transactions-pint/taxonomy.json)

Tavi JSON taxonomyはXBRL 2.1のXSD entry pointでもインスタンス文書でもありません。生成器と入力については、[Tavi生成器の説明](../tools/tavi/README_Tavi_4models_datatypes_candidate_ja.md)と[再現ガイド（英語）](../tavi-poc/README_REPRODUCE_4_MODELS.md)を参照してください。

公開条件と出所については[第三者資料の注意事項](../THIRD_PARTY_NOTICES_ja.md)を参照してください。
