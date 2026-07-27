# FSM→BSM→LHM/HMD基準環境のPrivate GitHub登録準備計画

## 1. 目的と範囲

FSMからBSMを生成し、BSMからLHM/HMDを生成するPoC処理について、仕様、program、
fixture、期待結果、試験及び再現記録が対応した基準環境を準備する。

今回の対象は次の二点に限定する。

1. 基本規則：FSM 14列、BSM 15列、LHM/HMD 17列、module-qualified Class、
   Association、Specialization、R／REF及び再現性。
2. element規則：semantic_pathによる意味識別、同名Classのmodule選択、
   prefixなしlowerCamelCase NCName、module内一意性及びR行のmultiplicity別要否。

syntax binding、profile、release manifest、taxonomy generator、taxonomy及びsampleの
実装は、この基準環境の登録と再現確認後に再開する。

## 2. 現行版と設計契約の区別

| 対象 | 現行契約 | 対応試験の実測 | 位置付け |
|---|---|---:|---|
| WORK `specialization.py` | 既存FSM入力、18列BSM出力 | native 4件合格 | 機能比較元。14／15列未対応 |
| WORK `graphwalk.py` | 旧15列BSM入力、旧19列LHM出力、DNM `-o`あり | native 2件合格 | 機能比較元。新15／17列未対応 |
| 単独4件版 | 旧15列BSM、旧19列LHM | 4件合格 | element及び空role等の部分比較 |
| 28件版 | 旧15列BSM、旧19列LHM | 28件合格 | formal header、Abstract、Reference、datatype等の比較 |
| 新PoC設計 | FSM 14列、BSM 15列、LHM/HMD 17列 | 受入試験案94件、未実装 | 登録候補を作る際の正式基準 |

既存版の試験合格は、その版が新契約へ対応したことを意味しない。4件又は28件という
件数では採否を決めず、各機能を新しい列契約のfixtureで再実装・再検証する。

## 3. 現行比較対象のSHA-256

| 世代 | ファイル | SHA-256 |
|---|---|---|
| WORK | `tools/semantic/specialization.py` | `4B793F71E8AD4E73604244DAC4DCBABFA4CA35811FC417EBA929A36209D7A85C` |
| WORK | `tools/semantic/graphwalk.py` | `B4508816E4B522F2468D89DEEDA24A0C7C238935FB08BC89A759071629FD2AEA` |
| WORK | `tests/test_specialization.py` | `3E9059E682CCB682552928721837854AD03FFC3FBBDF77F8C7BB09A8AADB60F4` |
| WORK | `tests/test_graphwalk.py` | `3BC08FEF13D7B76F68A2A44F03B317A2AA9551BE4B596C2ABE80197BD28FDB7A` |
| 4件版 | `programs/specialization.py` | `0E382BFCEEB4A1EC38DC90FE89AE96684363AB18AB8D4D87AF2256F7A56B15B7` |
| 4件版 | `programs/graphwalk.py` | `785A416C2A7E0E852F78551C9AE1D24BDBF5C6793BA652F14A362A65B70BF0F8` |
| 4件版 | `programs/test_xbrl_gl_next_2026.py` | `97A9739FA2931FD5A159E1AD0EC9D5A0785C9FE09C8D74D957535B88ECA55D79` |
| 28件版 | `programs/specialization.py` | `9E011931DE4F30C9EA9D8568B1BC174730A632728D006DF558F7A25DAF3BA2EF` |
| 28件版 | `programs/graphwalk.py` | `9B337CB9165483F5412B1187D8861D54E42F2C2DCA37645B82F3E982E9FD0C4D` |
| 28件版 | `programs/test_xbrl_gl_next_2026.py` | `6E9F38C313FA275D70A2E5AD0648949D97B69157DB91ACA1D792F06325B14C24` |

4件版及び28件版のpathはそれぞれ
`docs/ChatGPT/20260725_145244/programs/`及び
`docs/ChatGPT/20260725_153459/programs/`を基準とする。これらは来歴資料であり、
そのまま正式配置へコピーしない。

## 4. 登録対象

| 区分 | 登録候補 | 条件 |
|---|---|---|
| 基準仕様 | ADR-0005、ADR-0006、列契約、機能統合条件 | 基本規則とelement規則の記述が一致 |
| Specialization | 機能単位で統合した`specialization.py` | 14列FSM入力、15列BSM出力、対応fixture・期待結果・試験が揃う |
| Graph Walk | 機能単位で統合した`graphwalk.py` | 新15列BSM入力、17列LHM/HMD出力、対応fixture・期待結果・試験が揃う |
| fixture | 最小の合成FSM／BSM CSV | 実取引、個人情報、第三者原本及び未確認ライセンスを含まない |
| 期待結果 | 合成fixtureから生成するBSM／LHM/HMD | 手修正せず、生成commandとsource fixtureを記録 |
| 試験 | 単体試験及び受入試験 | 由来機能、入力条件、期待値、契約版を追跡可能 |
| 再現情報 | 実行環境、依存、command、終了code、SHA-256 | clean環境で二回実行して一致 |
| 制約 | 既知の制約と未実装事項 | syntax binding以降を実装済みと記載しない |

## 5. 除外対象

| 対象 | 理由 |
|---|---|
| `docs/ChatGPT/**`一式 | やり取りと来歴であり、正式な仕様・試験bundleではない |
| 28件版の同梱Excel及び生成済みfull BSM／LHM | 来歴、ライセンス及び実モデル範囲の確認が必要。新契約の期待値ではない |
| 正式FSM、既存BSM及び既存LHM/HMD | migration mapping、来歴及び新列契約への承認が未完了 |
| XBRL／UN/CEFACT由来XSD、XML、仕様書及びcode list | 再配布・改変条件が未解決 |
| instance、実取引CSV、個人情報を含み得るデータ | 匿名性、権利及び共有範囲が未確認 |
| taxonomy generator、taxonomy、sample | 今回の対象外 |
| cache、log、`__pycache__`、一時output | 再生成可能又は作業環境固有 |
| DNM `-o`及び`bie_to_fsm.py` | 新PoC pipelineの非対象 |

## 6. 要確認対象

1. 合成fixtureと期待結果に適用するproject license。
2. WORK、4件版及び28件版から移植する機能ごとの著作権表示。
3. canonical `id`を維持する範囲。elementの識別にはsemantic_pathを使用するが、
   今回の14／15／17列契約から`id`は削除しない。
4. 同名Classのmodule選択を与える最小の試験用入力形式。profile実装は今回行わない。
5. 命名衝突時に使用する承認済みelement mappingの最小形式。
6. 診断schema及びmanifestは後続方針であるため、今回の試験では必要最小限の
   machine-readable reportをどこまで含めるか。

## 7. ライセンス、秘密情報及び実データ

- `specialization.py`及び`graphwalk.py`はproject-authored MIT表示を確認済みであり、
  技術的には移植候補である。ただし、正式登録時は移植元と変更履歴を記録する。
- project-authored設計文書は既存のlicense方針に従う。
- 候補Python 10ファイルの簡易secret検索では秘密情報を検出していない。
  `token`という変数名は資格情報ではない。
- WORKのnative単体試験は一時ディレクトリ上の合成データを使用し、実取引データを
  必要としない。
- 既存Excel、full FSM／BSM／LHM及びinstanceは、権利・匿名性確認まで登録保留とする。

## 8. 推奨配置

```text
docs/
  architecture/
    semantic-model-column-contracts.md
  decisions/
    0005-semantic-core-element-and-association-identity.md
    0006-module-qualified-class-identity.md
  testing/
    semantic-functional-integration-conditions.md
    semantic-reproducibility.md
tools/
  semantic/
    specialization.py
    graphwalk.py
tests/
  semantic/
    specialization/
      fixtures/
      expected/
    graphwalk/
      fixtures/
      expected/
    acceptance/
reports/
  semantic-baseline/
    SHA256SUMS.txt
    TEST_RESULTS.md
```

fixtureと期待結果はprogramと同じcommit又は直前の試験commitで必ず対応付ける。
生成物だけを登録せず、入力、command、contract version及びSHA-256を併記する。

## 9. 推奨commit

1. 基準仕様書と列契約。
2. Specializationと対応fixture、期待結果及び試験。
3. Graph Walkと対応fixture、期待結果及び試験。
4. 再現環境、実行手順、SHA-256及び検証報告。

専用branch候補は`rearchitecture/oim-taxonomy-2026`とする。利用者確認前にbranchを
作成せず、`main`へ直接commit又はpushしない。GitHubのvisibility、remote又は
branch protectionも変更しない。

## 10. 再現基準

基準実行環境の初期候補はWindows、Python 3.10.2及びPython標準ライブラリである。
外部依存を追加する場合は版を固定し、必要理由を記録する。

各programについて次を満たす。

1. CLI help及び入力契約検査が成功する。
2. 単体試験及び受入試験が終了code 0で完了する。
3. 同一fixtureを独立した出力先へ二回処理する。
4. BSM及びLHM/HMDについてbyte単位のSHA-256が一致する。
5. 行数、列名、診断件数及び既知の除外を報告する。
6. 現行版からの機能移植元と、未実装の新契約項目を明示する。

## 11. 現時点の結論

仕様及び登録範囲は準備できるが、現行programをそのまま登録候補版とはしない。
現行三世代はいずれも新しい14／15／17列契約へ未対応である。利用者が本計画を
確認した後、WORK内の別統合候補領域でprogram、合成fixture、期待結果及び試験を
一体として作成する。
