[English](source-inventory.md) | **日本語**

# ソース台帳

## 目的と状態

このプロジェクト作成文書は、Private GitHub repositoryへ現在登録されている資料と、
WORK環境で計画中又は登録保留の資料を区別します。これは人が読むための登録概要で
あり、機械可読manifestでも、外部資産の再配布許可を示す証拠でもありません。

現在のPrivate repositoryには、2025年の検討資産と初期の再構築文書があります。
WORKで説明されている新しい`source/`、`taxonomy/`、`examples/`、
`tools/semantic/`及び生成台帳構造は、対象Git treeに実在しない限り登録済みとは
扱いません。

## 現在登録されているソース群

| 現在のGIT path | 役割 | 登録状態 |
| --- | --- | --- |
| `semantic-model/FSM/` | 2025年のFSM snapshot | 参照専用。14列PoC契約ではない |
| `semantic-model/BSM/` | 2025年のBSM snapshot | 参照専用。15列PoC契約ではない |
| `semantic-model/LHM/` | 2025年のLHM snapshot | 参照専用。17列LHM/HMD契約ではない |
| `scripts/` | 過去の変換及びtaxonomy script | 再利用前に機能・ライセンスreviewが必要 |
| `xBRL-CSV_taxonomy/` | 過去のxBRL-CSV taxonomy資料 | 参照専用。来歴・namespace reviewが必要 |
| `xBRL-CSV_instance/` | 過去のexample及びworkbook | 本計画以前に登録済み。権利、privacy及びtest状態のreviewが必要 |
| `XBRL-GL-2016-PWD/` | 過去のwork-product由来資料 | 外部条件が適用され、プロジェクト所有仕様ではない |
| `docs/` | プロジェクト文書及び設計判断 | Working Draft |
| `TaxonomyFramework/` | branch用に選定した再構築契約及び計画 | Working Draft |

既存ファイルは、適合性baseline又は回帰試験の期待値として自動的に採用しません。
来歴、ライセンス、データ機密性及び新14／15／17列契約との関係を個別にreviewします。

## 計画中・未登録

| 計画中のWORK資産群 | 予定用途 | 現在の判断 |
| --- | --- | --- |
| `contracts/` | consumer移行契約 | この候補はREADMEと空のmapping templateだけを含む |
| `source/models/core/` | semantic model入力候補 | 未登録 |
| `source/models/business-transactions/` | 取引文書model候補 | 未登録 |
| `source/unece/` | CCL由来分析入力 | source固有の権利確認まで登録保留 |
| `taxonomy/tuple/` | Tuple比較baseline | 新構成では未登録 |
| `taxonomy/oim/prototype/` | OIM／Palette技術prototype | 来歴、namespace及びライセンスreviewまで登録保留 |
| `taxonomy/experiments/` | Party、Document及びcode list実験 | 未登録 |
| `examples/vendor-invoice/` | end-to-end xBRL-CSV候補 | 未登録。データ・権利reviewが必要 |
| `tools/semantic/` | Specialization及びGraph Walk候補 | 未登録。program／fixture／test一式の承認が必要 |
| `tools/taxonomy/` | syntax-binding generator候補 | semantic baseline再現後まで延期 |
| `TaxonomyFramework/inventory/` | 機械可読Phase 0 evidence | 生成evidence。この候補には含めない |

## 外部参照baseline

| Work product | 状態 | Release date | 記録済み公式package SHA-256 |
| --- | --- | --- | --- |
| XBRL Global Ledger 2015 | Recommendation | 2015-03-25 | `AFCAEE16683E1D1348E0BBE91D1928EC5EF2265BEA8590238F86D52E9F12B931` |
| XBRL Global Ledger 2017 | Public Working Draft | 2016-12-01 | `0C48AA0EA8F6963CA5A3625AD32ADA6AEE5B3A164438A155A0C9937CCFFECE67` |

公式packageはsource、version及びchecksumで参照します。repository linkを満たす
ためだけにコピーしません。プロジェクトprototype及び過去のextractは、XBRL
Internationalの公式releaseではありません。

## 除外又は保留

- 再配布が明示的に確認できない外部ZIP及び標準文書
- 検証済みのdownload／再配布根拠がないUN/CEFACT由来BIE、code list又はtaxonomy
- 外部権利者のnamespaceを使用する改変XBRL由来taxonomy
- log、cache、bytecode、一時ファイル及び再生成可能な中間出力
- 実取引、個人情報、認証情報、機密設定及びconsumer working treeの内容
- 来歴が不明な重複又は日付付き作業copy

## 登録管理

1. 登録前にsource、version、checksum、権利状態、用途及びproject／external所有を記録する。
2. MIT又はCC BY 4.0は、識別済みのproject-authored資料だけに適用する。
3. 外部原本及び派生成果物には各権利者の条件を適用する。
4. 権利未解決資料はPrivate repositoryにも登録しない。
5. XBRL Japan、XBRL Europe、XBRL International、UN/CEFACTその他の組織による承認を推測しない。
6. コピー直前に対象branch及び実際のpathを再確認する。

ライセンス境界は[`../THIRD_PARTY_NOTICES_ja.md`](../THIRD_PARTY_NOTICES_ja.md)、
未解決の登録課題は
[`../TaxonomyFramework/OPEN_ISSUES_ja.md`](../TaxonomyFramework/OPEN_ISSUES_ja.md)
を参照してください。ADR-0003、ADR-0004及び詳細なPhase 0 inventory／dependency
reportは再評価中であり、この候補には登録しません。
