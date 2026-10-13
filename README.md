**English** | [日本語](README_ja.md)

# XBRL GL Next

## Purpose

This repository contains the XBRL GL Next Taxonomy Framework, the canonical semantic-model pipeline, purpose-specific HMD palettes, generated Tuple/OIM taxonomy samples, sample instances, and the tools and tests used to reproduce and validate the accepted packages. It also includes a Tavi proof of concept (PoC).

COR, BTX and AAA serve as reusable semantic **paint boxes**. A purpose-specific HMD is a **palette** that selects and organises semantics for a particular use. The Framework explores alternative taxonomy realisations—including XBRL 2.1 Tuple, OIM and Tavi—based on a common semantic foundation. Their implementation and acceptance states are distinct.

## Status

The current repository package is prepared for collaborative review. It has **not** been approved as a public release, standard, or official position of any organization.

The canonical project module namespace is `https://www.xbrl.or.jp/taxonomy/xbrl-gl-next/{module}`. The planned taxonomy version date `2026-12-31` remains in physical file names only and is not part of the namespace URI. The version date does not indicate that public release has already been approved.

See [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) for provenance and licence boundaries.

## Project phases

These project-level phases describe the overall review and publication lifecycle; they are **not** the implementation phases of the Tavi PoC.

### Phase 1 — Reproducible sample package

Phase 1 provides the first curated and reproducible XBRL GL Next sample package for collaborative review.

It includes:

- the Requirements Specification and the original Taxonomy Framework Parts 1–4 scope of the accepted sample package;
- the semantic-model pipeline from FSM through BSM, LHM and HMD-for-taxonomy;
- generated Tuple and OIM palette taxonomies;
- sample Tuple and OIM instances;
- the canonical tools and tests required to reproduce and validate that package.

The subsequent addition of Part 5 and the Tavi PoC does not retroactively extend the Phase 1 Tuple/OIM validation baseline. Phase 1 is a collaborative-review package and does not constitute approval for public release.

### Phase 2 — External collaborative review

Phase 2 is intended to use the Phase 1 package as the basis for review and coordination with relevant XBRL communities and other stakeholders.

The review is expected to cover, in particular:

- the semantic-model architecture;
- Specialisation, Graph Walk and the LHM/HMD processing model;
- the Tuple and OIM taxonomy bindings;
- the extension model and Aligned Pool;
- implementation reproducibility and validation.

Part 5 and the Tavi PoC provide additional, separately scoped material for review.

### Phase 3 — Publication candidate

Phase 3 is intended to incorporate the results of external review and prepare a publication candidate.

The Framework, taxonomy package, versioning, namespace usage, licensing and publication arrangements are expected to be stabilised for publication.

### Phase 4 — Public release and maintenance

Phase 4 is intended to cover public release and subsequent maintenance, including future versions, extensions, Aligned Pool maintenance and conformance-related updates.

## Framework documents

[`TaxonomyFramework/`](TaxonomyFramework/) contains the Requirements Specification, Taxonomy Framework Parts 1–5, and the inventory of registered sample artifacts. The five Parts have distinct roles:

- **Part 1 — General rules:** The serialisation-independent semantic pipeline and formal HMD contract.
- **Part 2 — Tuple palette taxonomy:** The XBRL 2.1 Tuple realisation from formal HMDs.
- **Part 3 — OIM palette taxonomy:** The OIM realisation from formal HMDs.
- **Part 4 — Aligned Pool and extension governance:** Semantic extension classification, alignment, registration and publication governance.
- **Part 5 — Tavi palette taxonomy:** Purpose-specific HMD views and their Tavi taxonomy and Table Template realisation.

Parts 2, 3 and 5 describe alternative taxonomy realisations rooted in the semantic foundation of Part 1 and governed, for extensions, by Part 4. This architectural relationship does not imply that all bindings share the same test or release status.

The formal Framework documents are maintained in English. [`TaxonomyFramework/README_ja.md`](TaxonomyFramework/README_ja.md) provides a Japanese guide.

## Canonical semantic pipeline

The semantic processing sequence is **FSM → BSM → Candidate LHM → Reviewed LHM → formal HMD → taxonomy bindings**. The transition from Candidate LHM to Reviewed LHM requires controlled human review; the reviewed source is not overwritten by automatic regeneration.

The published FSM and BSM sources include `semantic-model/FSM/FSM.csv`, `semantic-model/FSM/FSM_btx.csv` and `semantic-model/BSM/BSM.csv`. Candidate and reviewed LHM files are organised in root-specific directories under `semantic-model/LHM/`; the Accounting Entries and Business Transactions roots have both CSVs, while Journal Entries has a reviewed CSV governed by its accepted workbook. The formal Accounting Entries and Business Transactions HMD set and its manifest are in `semantic-model/LHM_for_taxonomy/`; Journal Entries has a separate HMD and manifest under `semantic-model/HMD/journal-entries/`. File existence and registered hashes do not by themselves establish a complete end-to-end reproduction or validation PASS. Select the accepted root-specific input and evidence before running the pipeline.

## Sample taxonomy and instances

The published taxonomy has three separate DTS trees, each with a Tuple and an OIM entry point (six taxonomy entry points in total; their existence does not assert six validation PASS results):

- `taxonomy/accounting-entries/`: Accounting Entries Tuple and OIM entry points
- `taxonomy/business-transactions/`: Business Transactions Tuple and OIM entry points
- `taxonomy/journal-entries/`: Journal Entries Tuple and OIM entry points

The sample instances under `ids/` comprise two Tuple instances in `ids/tuple/` and two xBRL-CSV reports in `ids/oim/`; each xBRL-CSV report uses its corresponding JSON metadata as the entry point. The number of sample reports is not the number of taxonomy entry points.

## Tavi PoC — Structured Tidy Data viewers

The [Tavi PoC](tavi-poc/) demonstrates two representations of the same Structured Tidy Data CSV using different Tavi definitions:

- [Simple Tavi Viewer](https://pontsoleil.github.io/XBRL_GL_Next/tavi-inst.html)
- [HMD View Viewer](https://pontsoleil.github.io/XBRL_GL_Next/tavi-inst-hmd-view.html)

Both self-contained Phase 1 HTML viewers display Table Template and Tavi taxonomy JSON sources in tabs on the left, and a transposed CSV on the right. This **Tavi PoC Phase 1** is separate from the repository's project-level Phase 1. JavaScript-based interactive Properties are planned for Tavi PoC Phase 2. The viewers do **not** perform formal XBRL/Tavi validation. See [`tavi-poc/README.md`](tavi-poc/README.md) for details and the current publication status of individual taxonomy files.

## Canonical tools

The following tools are present in the published repository and match the registered files; listing their paths does not assert that an entire current regression suite has passed:

- `tools/semantic/specialisation.py`
- `tools/semantic/graphwalk.py`
- `tools/semantic/post_graphwalk.py`
- `tools/semantic/validate_lhm.py`
- `tools/taxonomy/xBRLGL_TaxonomyGenerator.py`

The last file is the confirmed Tuple/OIM Taxonomy Generator implementation. No migration to `src/` has been substantiated. Verify applicable program specifications, input authority and acceptance evidence before execution.

## Taxonomy generation

The currently published generator supports this CLI syntax (implementation verified; this statement is not a new execution PASS):

```text
python tools/taxonomy/xBRLGL_TaxonomyGenerator.py \
  --hmd-dir <HMD_DIRECTORY> \
  --output-dir <TAXONOMY_OUTPUT_DIRECTORY> \
  --namespace <NAMESPACE>
```

The required `--namespace` argument takes a namespace anchor, for example `https://www.xbrl.or.jp/taxonomy/xbrl-gl-next/plt`. The positional `lhm_for_taxonomy` argument and `-b` / `--base-dir` remain available for backward compatibility. New automation should use `--hmd-dir` and `--output-dir` with the confirmed implementation.

## Canonical tests and validation

The accepted test inventory and relevant execution evidence must be checked before reproducing a package. Historical validation records reference different Arelle versions, input sets and entry-point scopes. **The Phase 1 Arelle validation baseline remains under review; no single numerical acceptance baseline is asserted in this README pending an evidence-based reconciliation** of execution IDs, input SHA-256 hashes, entry-point lists and results. Historical claims are not interchangeable with current acceptance. Consult the applicable package inventory and execution reports for the specifically tested configuration.

## Repository tree

```text
TaxonomyFramework/  Requirements Specification, Framework documents and inventory
semantic-model/     FSM and BSM; root-specific LHM and HMD resources
taxonomy/           Accounting Entries, Business Transactions and Journal Entries Tuple/OIM DTS trees
ids/                Tuple and xBRL-CSV sample instances
tavi-poc/           Tavi examples, taxonomy definitions and static HTML viewers
tools/              published semantic tools and confirmed Tuple/OIM generator (acceptance scoped per package)
tests/              canonical regression tests and package checker
```
