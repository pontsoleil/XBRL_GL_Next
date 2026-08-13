[English](README.md) | **日本語**

# Tools

このディレクトリには、XBRL GL Nextのセマンティックモデル変換を再現し、Tuple / OIMのサンプルtaxonomy packageを生成するための正式なPython toolsを格納しています。

規定上の根拠はXBRL GL Next Requirements SpecificationおよびTaxonomy Frameworkです。このディレクトリのscriptsは、それらの要求を実行・検証するための参照実装であり、Framework文書に代わるものではありません。

## 内容

```text
tools/
├─ semantic/
│  ├─ specialisation.py
│  ├─ graphwalk.py
│  ├─ post_graphwalk.py
│  └─ validate_lhm.py
└─ taxonomy/
   └─ xBRLGL_TaxonomyGenerator.py
```

### `semantic/specialisation.py`

1件以上の15列FSM CSVを読み込み、**Specialisation**を適用して16列BSMを生成します。Specialisation Associationに基づいて継承、追加、上書き、削除指定を処理し、Graph Walkの入力となるBSMを作成します。

```text
py tools/semantic/specialisation.py -h
```

### `semantic/graphwalk.py`

16列BSMと1つ以上の指定されたroot Classを入力として、18列の**candidate LHM**を生成します。Graph WalkはAssociationを決定論的に探索し、初期の`local_name`、`xpath`および診断情報を生成します。

```text
py tools/semantic/graphwalk.py -h
```

### `semantic/validate_lhm.py`

18列LHMの形式および整合性条件を検証します。人によるセマンティックレビューを代替するものではありません。

```text
py tools/semantic/validate_lhm.py -h
```

### `semantic/post_graphwalk.py`

人によるセマンティックレビューを完了した18列reviewed LHMを入力として、有効なlevel-1 rootごとに正式なHMD-for-taxonomy CSVを生成します。reviewed `local_name`と`multiplicity`を保持し、`xpath`を再生成したうえで、formal HMD-for-taxonomyの出力仕様への適合性を検証します。必要に応じて診断情報および`manifest.csv`も生成します。

```text
py tools/semantic/post_graphwalk.py -h
```

### `taxonomy/xBRLGL_TaxonomyGenerator.py`

`LHM_for_taxonomy`ディレクトリを入力として、TupleとOIMの両方を含むXBRL GL Nextの完全なtaxonomy packageを生成します。

taxonomy生成の正式入力は、`LHM_for_taxonomy`ディレクトリ直下に置かれたHMD-for-taxonomy CSVです。`manifest.csv`は実行結果を確認するための補助ファイルであり、taxonomyの内容を決定する入力ではありません。

```text
py tools/taxonomy/xBRLGL_TaxonomyGenerator.py -h
```

repository rootからの実行例:

```text
py tools/taxonomy/xBRLGL_TaxonomyGenerator.py semantic-model/LHM_for_taxonomy \
  -b <empty-output-directory> \
  -n http://www.xbrl.org/int/gl/plt/2026-12-31
```

出力directoryは空である必要があります。

## 処理の流れ

```text
FSM.csv + FSM_btx.csv
        |
        | Specialisation
        v
      BSM.csv
        |
        | Graph Walk
        v
 LHM_candidate.csv
        |
        | 人によるセマンティックレビュー
        v
XBRL_GL_Next_LHM_reviewed.csv
        |
        | Post-Graph Walk
        v
LHM_for_taxonomy/*.csv
        |
        | Taxonomy Generator
        v
taxonomy/  (Tuple + OIM)
```

candidate LHMからreviewed LHMへの移行は、人によるレビューを必要とする工程です。自動再生成やSHA-256の一致によって、このレビューを置き換えることはできません。

## 検証・編集方針

対応する回帰testおよびpackage checkerは[`../tests/`](../tests/)にあります。testを通すためだけに、生成済みsemantic-modelやtaxonomyを手作業で修正してはいけません。問題の原因となるmodelまたは処理工程を修正し、その後の成果物を再生成して検証をやり直します。
