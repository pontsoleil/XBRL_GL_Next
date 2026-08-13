[English](README.md) | **日本語**

# XBRL GL Next

## 目的

このrepositoryには、XBRL GL Next Taxonomy Framework、正式なセマンティックモデル・パイプライン、生成済みのTuple/OIMサンプルタクソノミ、サンプルinstance、およびそれらを再現・検証するためのtools/testsを収録しています。

## 状態

現在のrepository packageは共同レビュー用として整備したものです。public release、標準、またはいかなる組織の公式見解としても承認されていません。

taxonomy namespace/versionは`2026-12-31`です。このversion dateは、XBRL GL Nextを2026年中に完成しtaxonomyを公開する現在のプロジェクト計画を反映した予定version dateであり、public releaseが既に承認済みであることを意味しません。

来歴およびlicenseの境界は[THIRD_PARTY_NOTICES_ja.md](THIRD_PARTY_NOTICES_ja.md)を参照してください。

## プロジェクトのPhase

XBRL GL Nextは、段階的に開発・レビューを進めます。

### Phase 1 — 再現可能なサンプルパッケージ

Phase 1は、共同レビューのために整理した、最初の再現可能なXBRL GL Nextサンプルパッケージです。

次を含みます。

- Requirements SpecificationおよびTaxonomy Framework Part 1～4
- FSM → BSM → LHM → HMD-for-taxonomyのセマンティックモデル・パイプライン
- 生成したTuple / OIM palette taxonomy
- Tuple / OIMのサンプルinstance
- パッケージを再生成・検証するための正式なtoolsおよびtests

Phase 1は共同レビュー用のパッケージであり、public releaseの承認を意味するものではありません。

### Phase 2 — 外部共同レビュー

Phase 2では、Phase 1の成果物を基礎として、XBRL関係者その他の関係者とのレビューおよび調整を行うことを想定しています。

主なレビュー対象は次のとおりです。

- セマンティックモデルのアーキテクチャ
- Specialisation、Graph WalkおよびLHM/HMD処理
- Tuple / OIM taxonomy binding
- extension方式およびAligned Pool
- 実装の再現性および検証方法

### Phase 3 — Publication candidate

Phase 3では、外部レビューの結果を反映し、publication candidateを作成することを想定しています。

Framework、taxonomy package、version、namespace、license、公開方法などを、公開可能な状態に整理・固定します。

### Phase 4 — Public releaseと保守

Phase 4では、正式公開とその後の保守を想定しています。将来version、extension、Aligned Poolの保守、conformanceに関する更新などを含みます。

## Framework文書

`TaxonomyFramework/`には、Requirements Specification、Taxonomy Framework Part 1～4、および登録済みサンプル成果物のinventoryがあります。

正式なFramework文書は英語で管理します。`TaxonomyFramework/README_ja.md`では、このディレクトリにある文書を日本語で案内します。

## 正式semantic pipeline

```text
semantic-model/FSM.xlsx
  ↓ 正式FSM sheetをexport
semantic-model/FSM/FSM.csv + semantic-model/FSM/FSM_btx.csv
  ↓ tools/semantic/specialisation.py
semantic-model/BSM/BSM.csv
  ↓ tools/semantic/graphwalk.py
semantic-model/LHM/LHM_candidate.csv
  ↓ 人によるセマンティックレビュー
semantic-model/LHM/XBRL_GL_Next_LHM_reviewed.csv
  ↓ tools/semantic/post_graphwalk.py
semantic-model/LHM_for_taxonomy/*.csv
  ↓ tools/taxonomy/xBRLGL_TaxonomyGenerator.py
taxonomy/  (Tuple + OIM)
  ↓
ids/ sample instances
```

candidate LHMからreviewed LHMへの移行は、人によるレビューを必要とする工程です。reviewed LHMを自動再生成で上書きしません。reviewed LHMからHMDを経てtaxonomyに至る生成は決定論的です。

## サンプルtaxonomyおよびinstance

- `taxonomy/tuple/`: Tuple entry point 2件
- `taxonomy/oim/`: OIM entry point 2件
- `ids/tuple/`: Tuple sample instance 2件
- `ids/oim/`: xBRL-CSV sample 2件（各JSON metadata fileをreport entry pointとして使用）

## 正式tool

- `tools/semantic/specialisation.py`
- `tools/semantic/graphwalk.py`
- `tools/semantic/post_graphwalk.py`
- `tools/semantic/validate_lhm.py`
- `tools/taxonomy/xBRLGL_TaxonomyGenerator.py`

## 正式testおよび検証

- `tests/test_specialisation.py`
- `tests/test_graphwalk.py`
- `tests/test_semantic_pipeline.py`
- `tests/test_v5_taxonomy_generator.py`
- `tests/check_generated_package.py`

```powershell
py -m py_compile tools/semantic/specialisation.py tools/semantic/graphwalk.py tools/semantic/post_graphwalk.py tools/semantic/validate_lhm.py tools/taxonomy/xBRLGL_TaxonomyGenerator.py tests/test_specialisation.py tests/test_graphwalk.py tests/test_semantic_pipeline.py tests/test_v5_taxonomy_generator.py tests/check_generated_package.py
py -m pytest tests
py tests/check_generated_package.py taxonomy
```

Arelle 2.44.1によるtaxonomy entry point 4件およびsample instance entry point 4件の検証は別途実施します。受入済みvalidation baselineは`TaxonomyFramework/INVENTORY.md`を参照してください。

## Repository tree

```text
TaxonomyFramework/  Requirements Specification、Framework文書、inventory
semantic-model/     正式FSM → BSM → LHM → HMD成果物
taxonomy/           生成済みTuple/OIM sample taxonomy
ids/                TupleおよびxBRL-CSV sample instances
tools/              正式semantic/taxonomy generator
tests/              正式回帰testおよびpackage checker
```
