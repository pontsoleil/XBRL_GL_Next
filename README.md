**English** | [日本語](README_ja.md)

# XBRL GL Next

## Purpose

This repository provides a Phase 1 sample for understanding, reproducing, and validating the XBRL GL Next Taxonomy Framework. It contains the formal semantic-model chain, a generated Tuple/OIM taxonomy package, sample instances, and the canonical tools and tests needed to reproduce and verify them.

## Status

Inventory and validation were performed on 2026-08-12. The taxonomy namespace/version remains `2026-12-31`. The repository is a collaborative-review sample and has **not** been approved as a public release, standard, or official position of any organization.

See [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) for provenance and licence boundaries.

## Framework documents

`TaxonomyFramework/` contains the requirements specification, Parts 1–4 of the Taxonomy Framework, and `INVENTORY.md`, which records artifact hashes and the accepted validation baseline.

## Canonical semantic pipeline

```text
semantic-model/FSM.xlsx
  ↓ export formal FSM sheets
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

The candidate-to-reviewed LHM transition is a human review boundary. The reviewed LHM is not overwritten by automated regeneration. Generation from the reviewed LHM through the HMDs to the taxonomy is deterministic.

## Sample taxonomy and instances

- `taxonomy/tuple/`: two Tuple entry points
- `taxonomy/oim/`: two OIM entry points
- `ids/tuple/`: two Tuple sample instances
- `ids/oim/`: two xBRL-CSV samples, each using its JSON metadata file as the entry point

## Canonical tools

- `tools/semantic/specialization.py`
- `tools/semantic/graphwalk.py`
- `tools/semantic/post_graphwalk.py`
- `tools/semantic/validate_lhm.py`
- `tools/taxonomy/xBRLGL_TaxonomyGenerator.py`

## Taxonomy generation

The formal recommended CLI for the Taxonomy Generator is:

```text
python tools/taxonomy/xBRLGL_TaxonomyGenerator.py \
  --hmd-dir <HMD_DIRECTORY> \
  --output-dir <TAXONOMY_OUTPUT_DIRECTORY> \
  --namespace <NAMESPACE>
```

The positional `lhm_for_taxonomy` argument and `-b` / `--base-dir` remain available for backward compatibility. New automation should use `--hmd-dir` and `--output-dir`.

## Canonical tests and validation

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

Phase 1 regression validation used Arelle 2.37.77 for all four formal taxonomy entry points (two Tuple and two OIM): 4/4 passed with error 0 and warning 0. See `TaxonomyFramework/INVENTORY.md` for the accepted validation baseline.

## Repository tree

```text
TaxonomyFramework/  requirements, Framework documents, and inventory
semantic-model/     canonical FSM → BSM → LHM → HMD artifacts
taxonomy/           generated Tuple/OIM sample taxonomy
ids/                Tuple and xBRL-CSV sample instances
tools/              canonical semantic and taxonomy generators
tests/              canonical regression tests and package checker
```
