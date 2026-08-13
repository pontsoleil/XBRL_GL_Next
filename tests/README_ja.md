[English](README.md) | **日本語**

# Tests

このディレクトリには、XBRL GL Nextのセマンティックパイプラインおよび生成taxonomy packageに対する、正式に保持する自動検証を格納しています。

これらのtestsは、実装適合性と回帰管理を支援します。規定上の根拠はRequirements SpecificationおよびTaxonomy Frameworkです。

## 内容

```text
tests/
├─ README.md
├─ README_ja.md
├─ test_specialisation.py
├─ test_graphwalk.py
├─ test_semantic_pipeline.py
├─ test_v5_taxonomy_generator.py
└─ check_generated_package.py
```

### `test_specialisation.py`

FSMからBSMへの**Specialisation変換処理**を検証します。正規のSpecialisation Associationの処理、旧綴り`Specialization`の正規化、削除指定の処理、およびBSMが決定論的に生成されることなどを確認します。

### `test_graphwalk.py`

16列のBSMから18列のcandidate LHMを生成する**Graph Walk処理**を検証します。指定rootからの決定論的な探索、`source_bsm_id`再利用の診断、`local_name`と`xpath`の生成、および名前衝突などの診断を確認します。

### `test_semantic_pipeline.py`

FSMからBSM、candidate LHM、reviewed LHM、HMD-for-taxonomy、taxonomy生成までの一連の処理を検証します。

candidate LHMからreviewed LHMへの移行は、人によるセマンティックレビューを必要とする工程です。このtestは、その人によるレビューを代替するものではありません。

### `test_v5_taxonomy_generator.py`

正式なtaxonomy generatorに対する回帰testです。18列HMDの入力仕様、`0..0`による非使用部分木の除外、複数HMDの処理、TupleとOIMの分離、bindingごとのmodule presentation、OIMの`p_` Class primary item、および決定論的なtaxonomy生成などを検証します。

### `check_generated_package.py`

受入済みのformal 56-file taxonomy packageを検査する、単独実行可能な静的検査toolです。

package構成、local reference、locator fragmentの解決、Tuple/OIM DTSの分離、bindingごとのmodule presentation、OIM module schema、dimensional locator、およびlocator / presentation arcの重複などを検査します。

`taxonomy/README.md`および`taxonomy/README_ja.md`などのrepository説明文書は、formal 56-file taxonomy packageには含めません。

## テストの実行

repository rootから、`pytest`をインストールした環境で実行します。

```text
py -m pytest tests
```

2026-08-12の受入baseline:

```text
63 passed
```

passed件数は参考値です。本質的な合格条件はfailureが0、collection/runtime errorが0であることです。

package checkerは別に実行します。

```text
py tests/check_generated_package.py taxonomy
```

受入baseline:

```text
formal taxonomy files: 56
local references checked: 3,821
unresolved local files: 0
unresolved local fragments: 0
dimensional locators checked: 850
failures: 0
```

## 外部processorによる検証

Python testsはXBRL processorによる検証を代替しません。2026-08-12の受入baselineでは、さらに次を確認しています。

- Arelle 2.44.1: taxonomy entry point 4件、error 0 / warning 0
- Arelle 2.44.1: sample instance 4件、error 0 / warning 0
- XMLSpy GUI: Tuple / OIM DTS確認済み

## テストを実行する時点

semantic-processing tool、formal semantic-model artefact、taxonomy generator、generated taxonomy、またはreport validationに影響するsample instanceを変更した場合は、関連testを実行してください。正式登録前には保持する全test suiteとpackage checkerを実行します。

## failureの扱い

testを通すためだけに生成成果物を手修正してはいけません。failureがsemantic model、processing tool、taxonomy generator、test expectation、sample dataのどこに属するかを特定し、責任を持つsourceを修正して下流検証を再実行します。
