**English** | [日本語](README_ja.md)

# XBRL GL Next

## Purpose

This repository contains the XBRL GL Next Taxonomy Framework, the canonical semantic-model pipeline, generated Tuple/OIM taxonomy samples, sample instances, and the tools and tests needed to reproduce and validate them.

## Status

The current repository package is prepared for collaborative review. It has **not** been approved as a public release, standard, or official position of any organization.

The taxonomy namespace/version remains `2026-12-31`. The version date reflects the current project plan to complete XBRL GL Next and publish the taxonomy within 2026; it does not indicate that public release has already been approved.

See [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) for provenance and licence boundaries.

## Project phases

XBRL GL Next is being developed and reviewed in stages.

### Phase 1 — Reproducible sample package

Phase 1 provides the first curated and reproducible XBRL GL Next sample package for collaborative review.

It includes:

- the Requirements Specification and Taxonomy Framework Parts 1–4;
- the semantic-model pipeline from FSM through BSM, LHM and HMD-for-taxonomy;
- generated Tuple and OIM palette taxonomies;
- sample Tuple and OIM instances;
- the canonical tools and tests required to reproduce and validate the package.

Phase 1 is a collaborative-review package and does not constitute approval for public release.

### Phase 2 — External collaborative review

Phase 2 is intended to use the Phase 1 package as the basis for review and coordination with relevant XBRL communities and other stakeholders.

The review is expected to cover, in particular:

- the semantic-model architecture;
- Specialisation, Graph Walk and the LHM/HMD processing model;
- the Tuple and OIM taxonomy bindings;
- the extension model and Aligned Pool;
- implementation reproducibility and validation.

### Phase 3 — Publication candidate

Phase 3 is intended to incorporate the results of external review and prepare a publication candidate.

The Framework, taxonomy package, versioning, namespace usage, licensing and publication arrangements are expected to be stabilized for publication.

### Phase 4 — Public release and maintenance

Phase 4 is intended to cover public release and subsequent maintenance, including future versions, extensions, Aligned Pool maintenance and conformance-related updates.

## Framework documents

`TaxonomyFramework/` contains the Requirements Specification, Taxonomy Framework Parts 1–4, and the inventory of the registered sample artifacts.

The formal Framework documents are maintained in English. `TaxonomyFramework/README_ja.md` provides a Japanese guide to the documents in that directory.

## Canonical semantic pipeline

```text
semantic-model/FSM.xlsx
  ↓ export formal FSM sheets
semantic-model/FSM/FSM.csv + semantic-model/FSM/FSM_btx.csv
  ↓ tools/semantic/specialisation.py
semantic-model/BSM/BSM.csv
  ↓ tools/semantic/graphwalk.py
semantic-model/LHM/LHM_candidate.csv
  ↓ human semantic review
semantic-model/LHM/XBRL_GL_Next_LHM_reviewed.csv
  ↓ tools/semantic/post_graphwalk.py
semantic-model/LHM_for_taxonomy/*.csv
  ↓ tools/taxonomy/xBRLGL_TaxonomyGenerator.py
taxonomy/  (Tuple + OIM)
  ↓
ids/ sample instances
```

The candidate-to-reviewed LHM transition is a human-review boundary. The reviewed LHM is not overwritten by automated regeneration. Generation from the reviewed LHM through the HMDs to the taxonomy is deterministic.

## Sample taxonomy and instances

- `taxonomy/tuple/`: two Tuple entry points
- `taxonomy/oim/`: two OIM entry points
- `ids/tuple/`: two Tuple sample instances
- `ids/oim/`: two xBRL-CSV samples, each using its JSON metadata file as the report entry point

## Canonical tools

- `tools/semantic/specialisation.py`
- `tools/semantic/graphwalk.py`
- `tools/semantic/post_graphwalk.py`
- `tools/semantic/validate_lhm.py`
- `tools/taxonomy/xBRLGL_TaxonomyGenerator.py`

## Canonical tests and validation

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

Arelle 2.44.1 is used separately to validate the four taxonomy entry points and four sample-instance entry points. See `TaxonomyFramework/INVENTORY.md` for the accepted validation baseline.

## Repository tree

```text
TaxonomyFramework/  Requirements Specification, Framework documents and inventory
semantic-model/     canonical FSM → BSM → LHM → HMD artifacts
taxonomy/           generated Tuple/OIM sample taxonomy
ids/                Tuple and xBRL-CSV sample instances
tools/              canonical semantic and taxonomy generators
tests/              canonical regression tests and package checker
```
