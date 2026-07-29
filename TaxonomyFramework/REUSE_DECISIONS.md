# 旧資産のファイル単位再利用判定

## 1. 対象と前提

対象は[pontsoleil/XBRL_GL_Next](https://github.com/pontsoleil/XBRL_GL_Next)の
commit `4172d5f77c61ec7bc3ec7e68d77afb52b752bdbd`に含まれる追跡対象370ファイルである。

評価の入力には、次の検証済みバックアップ台帳を使用した。

```text
C:\Users\nobuy\GitHub\GIT\XBRL_GL_Next_BACKUP\20260725_4172d5f
```

バックアップ、正式リポジトリ及びUADAのファイルは変更していない。旧BSM及びLHMは
正解データではなく、差分、設計意図、来歴及び互換性確認用の資料として扱う。

## 2. 判定結果

| 判定 | 件数 | 意味 |
|---|---:|---|
| `reuse_as_is` | 1 | 内容を維持して再利用 |
| `adapt_and_reuse` | 31 | 新契約へ変換して再利用 |
| `reference_only` | 19 | 来歴・比較資料として保存 |
| `replace` | 7 | 新構成に合わせて作り直す |
| `exclude` | 0 | 現時点で確定除外なし |
| `needs_license_review` | 308 | 上流権利条件の確認後に採否確定 |
| `needs_design_decision` | 4 | 新しい責務・CLI・利用範囲の決定が必要 |

`needs_license_review`の大部分は、XBRL Internationalの著作権表示を含む
`XBRL-GL-2016-PWD` 275ファイル及び旧OIM taxonomyのXSD/XMLである。技術的な
再利用性を否定する判定ではなく、正式コピーの前提条件を示す。

## 3. 優先対象の判断

### 3.1 semantic-model/FSM

判定: `adapt_and_reuse`

旧FSM 418行及びJPN拡張84行は、概念、定義、association及び地域固有定義の比較元として
使用する。今回の正式入力であるreview済みFSM 500行＋FSM_btx 77行へ直接連結しない。

必要な作業:

- 旧概念と新Shared/Aligned FSMの一対一・統合・分割・廃止対応を作成する。
- JPN拡張をAlignedとして再分類する。
- 正式FSMヘッダー、module、logical class参照、Abstract Class及びmultiplicity規則へ変換する。
- XBRL GL由来定義の出典及び改変履歴を記録する。

### 3.2 specialization.py

旧正式版全体の判定: `adapt_and_reuse`

WORK版、単独4件版及び28件版を機能単位で比較する。いずれか一版をそのまま
正式統合候補とせず、extension入出力は要件として再評価し、必要な場合だけ移植する。

| 機能 | WORK版 | 4件版 | 28件版 | 判断 |
|---|---|---|---|---|
| FSMヘッダー正規化 | 基本header | 部分候補 | formal header alias | 28件版機能を移植候補 |
| Specialization | 実装あり | 実装あり | 実装・広い回帰あり | JIS規則で3版を比較 |
| Association同一性 | 空roleを拒否 | 空role fixtureあり | role＋associated class | 新契約の`(association_role, associated_module, associated_class)`へ置換し、`property_term`をidentityから除外。空roleを許容し、同一key重複を報告。PoCでは曖昧propertyを未反映として他を継続 |
| multiplicity 0削除 | 実装あり | 実装あり | `0`及び`0..0`対応 | 共通機能として回帰 |
| Abstract Class | 基本処理 | 検査あり | 参照を報告・除外 | 28件版機能を移植候補 |
| 未定義Class参照 | 世代依存 | 検査あり | 事前検査あり | 入力エラー契約へ統合 |
| extension FSM/BSM | 個別CLIあり | なし | 統合入力中心 | 要件決定後に必要部分のみ移植 |
| CLI/入出力 | 18列BSM | 15列BSM | 15列BSM | FSM 15列／BSM 16列へ移行し、追加項目はsidecarへ分離 |

### 3.3 graphwalk.py

旧正式版全体の判定: `adapt_and_reuse`

| 機能 | WORK版 | 4件版 | 28件版 | 判断 |
|---|---|---|---|---|
| BSMヘッダー | 15列入力だがspecialization 18列出力と不整合 | 15列 | 15列 | FSM 15列＋`id`の16列canonical契約承認後に接続 |
| module／logical class | QName／先頭3文字推測あり | 推測が残る | 厳密QName処理 | QName処理は移植せず、`(module, class_term)`及び`(associated_module, associated_class)`検査へ置換 |
| syntax binding QName | graph walkへ混在 | 一部混在 | 厳密処理 | taxonomy generator側のsyntax binding責務として再設計 |
| 未定義参照 | 探索時依存 | 改善途中 | 到達不能を含む事前検査 | 入力エラー契約へ統合 |
| Graph Walk | 実装あり | 実装あり | 主要比較基準 | 規則別に3版を比較 |
| 複数root | 対応 | 対応 | 対応 | root順序と重複を回帰 |
| Reference R/REF | 旧処理 | R/REF処理 | R/REF後に探索停止 | 28件版機能を移植候補 |
| datatype | 旧更新処理 | 保持改善 | Attribute/REF保持 | 28件版を基礎に実データ確認 |
| semantic path | 旧生成・重複回避 | 改善あり | 19列候補 | 17列coreで維持し、`path`／`abbreviation_path`／`xpath`／`associated_class`を廃止 |
| element名 | abbreviation/index処理 | 部分改善 | semantic path後に生成 | LC3、重複語除去、先祖前置及び全体一意性を採用 |
| DNM `-o` | 実装あり | なし | なし | 非サポート。後続実装でCLI、分岐、出力、例及び専用testを削除 |
| CLI/入出力 | DNMを含む | 19列LHM | 19列LHM | 17列LHM canonical coreへ統合。HMDはbinding段階で選択 |

旧正式版の`specialization.py`及び`graphwalk.py`は`common.utils`をimportするが、正式
リポジトリ内に対応配置を確認できない。ファイル全体の直接コピーは行わない。

### 3.4 xBRLGL_TaxonomyGenerator.py

判定: `needs_design_decision`

| 機能単位 | 初期判断 | 主な確認事項 |
|---|---|---|
| schema生成 | `adapt_and_reuse`候補 | 新LHM列、Shared/Aligned module、OIM concept |
| concept/type生成 | `adapt_and_reuse`候補 | datatype、periodType、substitutionGroup |
| dimension/domain/member | `adapt_and_reuse`候補 | OIMモデルと重複概念の扱い |
| hypercube | `adapt_and_reuse`候補 | root別閉包、closed/contextElement |
| definition linkbase | `adapt_and_reuse`候補 | arcrole、targetRole、role URI |
| label/reference | `adapt_and_reuse`候補 | 多言語、出典及びreference role |
| xBRL-CSV metadata | `adapt_and_reuse`候補 | OIM仕様、table/column mapping |
| namespace/URI管理 | `replace` | 2025-12-01固定値を廃止し2026-12-31設定を一元化 |
| entry point生成 | `adapt_and_reuse`候補 | Palette/OIM dual supportの正式entry point |
| DTS検証 | `replace` | 生成器内部に十分な合否処理がなく、XML Schema及びXBRL validationを独立化 |

文字列生成ロジックをそのまま採用せず、生成物単位のコンポーネントへ分割して試験する。

### 3.5 xBRL-CSV_taxonomy

JSON及びskeleton CSVは`adapt_and_reuse`、XSD/XMLは`needs_license_review`とした。
XMLSpy及びXBRL validationが可能な旧基準として保存価値が高い。

新正式タクソノミへ直接上書きせず、次を比較する。

- entry pointとDTS閉包
- namespace及び2025-12-01の日付
- PaletteとOIMのdual support構造
- dimension、domain、member及びhypercube
- label、reference、presentation及びdefinition
- xBRL-CSV metadataとskeleton

### 3.6 xBRL-CSV_instance

23ファイルを`adapt_and_reuse`とした。仕訳、請求、固定資産、予算実績、勤怠等を含み、
新タクソノミの分野横断性を検証できる。

正式移植前に、ライセンス、個人情報、実取引情報、JSON/CSVの対応、期待fact/aspect及び
新taxonomy URIを確認する。

### 3.7 XBRL-GL-2016-PWD

275ファイルを`needs_license_review`とした。全ファイルを新正式構成へコピーする判断ではない。
旧Tuple/Paletteの意味、module、label、presentation及びentry pointを確認する参照基準として
評価する。XBRL Internationalのlegal termsを確認後、同梱、外部参照又は除外を決定する。

### 3.8 旧BSM及びLHM

BSM 2ファイル及びLHM 14ファイルは`reference_only`である。新生成物の行数又は期待値として
採用しない。生成元、旧スクリプト、手修正、root及びPalette構成を特定したうえで、全行差分に
使用する。

### 3.9 旧文書、bat及び試験

旧文書3ファイルは`reference_only`、README及びbat 6ファイルは`replace`とした。batには
現行リポジトリと一致しない相対パスがあり、自動的な合否判定も不足する。利用シナリオだけを
新しいunit/integration/XBRL validation試験へ移植する。

## 4. 試験資産の世代

### 28件版

所在:

```text
C:\Users\nobuy\GitHub\WORK\XBRL-GL-Next\docs\ChatGPT\20260725_153459
```

| ファイル | SHA-256 |
|---|---|
| `programs/specialization.py` | `9e011931de4f30c9ea9d8568b1bc174730a632728d006df558f7a25daf3ba2ef` |
| `programs/graphwalk.py` | `9b337cb9165483f5412b1187d8861d54e42f2c2dca37645b82f3e982e9fd0c4d` |
| `programs/test_xbrl_gl_next_2026.py` | `6e9f38c313fa275d70a2e5ad0648949d97b69157db91aca1d792f06325b14c24` |

### 状況報告上の31件版

31件合格の状況報告は過去の参考記録とする。現在のWORKでは、3ファイル一式、
対応fixture及び実行条件を再現できないため、正式統合候補、回帰baseline又は
完了条件にしない。不足物を探索又は他版から推測して再作成しない。

正式版は、WORK 6件、単独4件、28件及びGitHub実データ試験から必要機能を選び、
新しい試験集合として件数を確定する。

## 5. ライセンス上の注意

- プロジェクトのPythonスクリプトはMIT Licenseと明記されている。
- 文書及び生成成果物はリポジトリの`LICENSE.md`でCC BY 4.0とされている。
- XBRL-GL-2016-PWD及び旧taxonomyの多くにはXBRL Internationalの著作権表示がある。
- リポジトリ側のCC BY 4.0宣言だけで上流権利条件を置き換えたとは判断しない。
- 正式コピー前にXBRL Internationalのlegal terms、改変表示、帰属表示及び再配布条件を確認する。
- instanceは権利に加えて個人情報及び実取引情報の有無を確認する。

## 6. 未決事項

1. 旧FSM及び生成taxonomyに含まれるXBRL GL定義の再配布条件。
2. 旧BSM/LHMの機械生成後の手修正有無。
3. 旧extension FSM/BSM及び複数rootを新正式CLIに含める範囲。
4. FSM 15列、BSM 16列、LHM/HMD 17列契約、HMD選択及びtaxonomy generator入力契約。
5. 新OIM taxonomyのnamespace、2026-12-31 URI及びentry point命名。
6. 旧instanceを公開回帰試験として使用できるか。
7. WORK版、4件版及び28件版から作る統合候補の作業場所とfixture配置。
