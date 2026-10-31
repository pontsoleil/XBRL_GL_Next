**English** | [日本語](README_ja.md)

# XBRL GL Next

XBRL GL Next explores a common semantic foundation and purpose-specific **HMD palettes** that can be realised as XBRL 2.1 Tuple, OIM, or experimental Tavi JSON taxonomies. COR, BTX and AAA are reusable semantic **paint boxes**, not interchangeable instance formats. This repository is material for collaborative review, not a claim of formal adoption by any standards organisation.

## Status and project phases

This is a collaborative-review package, not an approved standard, a public release endorsement or an official position of any organisation. The project-level phases below are **not** the Tavi PoC's own phases.

- **Phase 1 — Reproducible sample package:** Requirements and Parts 1–4, semantic pipeline, Tuple/OIM taxonomies, samples, tools and tests for the accepted scope. Part 5 is a separately registered Tavi collaborative draft and does not retroactively expand the earlier Phase 1 acceptance.
- **Phase 2 — External collaborative review:** Review of semantic architecture, Specialisation, Graph Walk, extension governance and Tuple/OIM bindings.
- **Phase 3 — Publication candidate:** Incorporation of review findings and preparation of versioning, namespace, licensing and publication arrangements.
- **Phase 4 — Public release and maintenance:** Approved publication followed by maintenance, future versions and aligned extensions.

See [third-party notices](THIRD_PARTY_NOTICES.md) for attribution and licence boundaries.

## Read the specification first

- [Taxonomy Framework](TaxonomyFramework/README.md): Requirements Specification and Parts 1–5 (each with its own draft and acceptance status).
- **Part 1 — General rules:** semantic pipeline and the formal HMD contract.
- **Part 2 — Tuple palette taxonomy:** XBRL 2.1 Tuple binding.
- **Part 3 — OIM palette taxonomy:** dimensional/OIM binding and xBRL-CSV representation.
- **Part 4 — Aligned Pool:** governance for extensions of the Shared semantic models.
- **Part 5 — Tavi palette taxonomy:** purpose-specific HMD views and Tavi binding. Its registered draft does not by itself establish implementation conformance; consult the separate PoC evidence.

## Semantic processing

Shared COR classes are specialised by the COR-JPN Aligned extension; Shared BTX classes are specialised by the BTX-PINT Aligned extension. These four HMD/taxonomy results remain independent. The processing sequence is **FSM → Specialisation / BSM → Graph Walk → Candidate LHM → human Reviewed LHM → Post-Graph Walk → formal HMD → taxonomy generation**. The Journal Entry Tavi discussion candidate is a separately scoped HMD view.

See [semantic-model/README.md](semantic-model/README.md) for authority boundaries and [tools/README.md](tools/README.md) for implementations.

## Taxonomies and examples

- [taxonomy/README.md](taxonomy/README.md) — separate Accounting Entries, Business Transactions and Journal Entries Tuple/OIM DTS trees, and the separately scoped Journal Entry Tavi discussion draft.
- [ids/README.md](ids/README.md) — **`ids` stands for XBRL Instance Documents**, not identifier definitions. `ids/tuple/` contains XBRL 2.1 XML sample instances; `ids/oim/` contains xBRL-CSV reports with corresponding JSON metadata. **The JSON metadata is the report entry point**, and the data CSV and metadata are a pair.
- [tavi-poc/README.md](tavi-poc/README.md) — the Journal Entry PWD discussion taxonomy and its static viewer. Experimental discussion draft based on Tavi PWD 2026-09-01; formal conformance has not been established.

## Reproduce and validate

- [tools/README.md](tools/README.md) — scripts, applicable Framework parts and actual input/output contracts.
- [tests/README.md](tests/README.md) — existing tests, how to identify dependencies and why historical acceptance must not be assumed to be a current test PASS.
- [definitions/README.md](definitions/README.md) — code lists, datatype and overlay definitions (only when the consuming tool explicitly reads them).

## Publication status and evidence

Experimental discussion draft based on Tavi PWD 2026-09-01; formal conformance has not been established. The only published Tavi taxonomy is the [Journal Entry JSON](tavi-poc/taxonomy/Tavi_JournalEntries_SingleAccount_Date_r2_candidate.json), with its Table Template embedded. The [Journal Entry viewer](https://pontsoleil.github.io/XBRL_GL_Next/tavi-inst-hmd-view.html) is a static display, not a conformance validator. Earlier Tavi models, report metadata and Arelle patches are withdrawn; originals and historical evidence remain in WORK.

[Third-party notices](THIRD_PARTY_NOTICES.md)

## Tuple/OIM taxonomy generator CLI

The existing generator has this documented interface (a description, not evidence of a new run):

``text
python tools/taxonomy/xBRLGL_TaxonomyGenerator.py \
  --hmd-dir <HMD_DIRECTORY> \
  --output-dir <TAXONOMY_OUTPUT_DIRECTORY> \
  --namespace <NAMESPACE>
``

The required namespace anchor may be `https://www.xbrl.or.jp/taxonomy/xbrl-gl-next/plt`. The positional HMD input and `-b`/`--base-dir` are retained for compatibility in the verified older contract.

## Scope of validation evidence

The Phase 1 Arelle baseline remains under review for reconciled execution IDs, input hashes, entry-point lists and result scopes; no single universal numerical acceptance baseline is asserted. Historical results do not amount to a new test execution.
