[English](README.md) | **日本語**

# XBRL GL Next

## 目的

このrepositoryは、XBRL GL Next Taxonomy Frameworkを理解し、再現し、検証するためのPhase 1 sampleです。正式semantic-model chain、生成済みTuple/OIM taxonomy package、sample instance、及び再現・検証に必要な正式tool/testを収録します。

## 状態

棚卸し及び検証日は2026-08-12です。taxonomy namespace/versionは`2026-12-31`のままです。本repositoryはcollaborative-review sampleであり、public release、標準、又はいかなる組織の公式見解としても承認されていません。

来歴及びlicense境界は[THIRD_PARTY_NOTICES_ja.md](THIRD_PARTY_NOTICES_ja.md)を参照してください。

## Framework文書

`TaxonomyFramework/`には、要求仕様、Taxonomy Framework Part 1～4、及び成果物SHAと受入済み検証baselineを記録する`INVENTORY.md`があります。

## 正式semantic pipeline

```text
semantic-model/FSM.xlsx
  ↓ 正式FSM sheetをexport
semantic-model/FSM/FSM.csv + semantic-model/FSM/FSM_btx.csv
  ↓ tools/semantic/specialization.py
semantic-model/BSM/BSM.csv
  ↓ tools/semantic/graphwalk.py
semantic-model/LHM/LHM_candidate.csv
  ↓ human review
semantic-model/LHM/XBRL_GL_Next_LHM_reviewed.csv
  ↓ tools/semantic/post_graphwalk.py
semantic-model/LHM_for_taxonomy/*.csv
  ↓ tools/taxonomy/xBRLGL_TaxonomyGenerator.py
taxonomy/  (Tuple + OIM)
  ↓
ids/ sample instances
```

candidate LHMからreviewed LHMへの遷移は人手reviewの境界です。reviewed LHMを自動再生成で上書きしません。reviewed LHMからHMDを経てtaxonomyに至る生成はdeterministicです。

## Sample taxonomy及びinstance

- `taxonomy/tuple/`: Tuple entry point 2件
- `taxonomy/oim/`: OIM entry point 2件
- `ids/tuple/`: Tuple sample instance 2件
- `ids/oim/`: xBRL-CSV sample 2件（各JSON metadataをentry pointとして使用）

## 正式tool

- `tools/semantic/specialization.py`
- `tools/semantic/graphwalk.py`
- `tools/semantic/post_graphwalk.py`
- `tools/semantic/validate_lhm.py`
- `tools/taxonomy/xBRLGL_TaxonomyGenerator.py`

## 正式test及び検証

- `tests/test_specialization.py`
- `tests/test_graphwalk.py`
- `tests/test_semantic_pipeline.py`
- `tests/test_v5_taxonomy_generator.py`
- `tests/check_generated_package.py`

```powershell
py -m py_compile tools/semantic/specialization.py tools/semantic/graphwalk.py tools/semantic/post_graphwalk.py tools/semantic/validate_lhm.py tools/taxonomy/xBRLGL_TaxonomyGenerator.py tests/test_specialization.py tests/test_graphwalk.py tests/test_semantic_pipeline.py tests/test_v5_taxonomy_generator.py tests/check_generated_package.py
py -m pytest tests
py tests/check_generated_package.py taxonomy
```

Arelle 2.44.1によるtaxonomy entry point 4件及びsample instance entry point 4件の検証は別途実施します。受入済みbaselineは`TaxonomyFramework/INVENTORY.md`を参照してください。

## Repository tree

```text
TaxonomyFramework/  要求仕様、Framework文書及び台帳
semantic-model/     正式FSM → BSM → LHM → HMD成果物
taxonomy/           生成済みTuple/OIM sample taxonomy
ids/                Tuple及びxBRL-CSV sample instances
tools/              正式semantic/taxonomy generator
tests/              正式回帰test及びpackage checker
```
