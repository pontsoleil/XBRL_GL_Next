# XBRL GL Next canonical WORK taxonomy

The active taxonomy consists of two independently generated DTS trees:

- `accounting-entries/` (58 files)
- `business-transactions/` (67 files)

Every project module uses the exact stable namespace `https://www.xbrl.or.jp/taxonomy/xbrl-gl-next/{module}`. The date `2026-12-31` remains in file names as the planned taxonomy version and is not part of a namespace URI. The project publication and namespace decision is recorded in `PROJECT_PUBLICATION_AND_NAMESPACE_DECISION.md`. That record states the decision maker's project role and does not claim a separate board resolution, domain-administrator delegation, official taxonomy designation, or external endorsement.

Accounting Entries and Business Transactions intentionally remain split because each is expanded from a different root HMD. Fourteen shared global declarations have root-HMD-specific type, structure, or multiplicity differences. These differences are accepted characteristics of the separate DTSs, not conflicts or defects. Load each DTS from its corresponding Tuple or OIM entry point; do not overwrite same-named files or mix the DTSs without an explicit integration design. Single-DTS combined use is outside the accepted scope.

The former root-level single taxonomy tree was moved to `../archive/taxonomy/legacy-single-tree-20260915_1406/`. It is retained for evidence and is outside the active `taxonomy/**` tree.

Generation evidence and SHA-256 manifests are under `provenance/`. Validation evidence is under `C:\Users\nobuy\GitHub\WORK\XBRL-GL-Next\docs\Codex\2026\202609\20260915\20260915_1406\stable-namespace-work-unification\outputs`.

The XBRL GL source, copyright, licence conditions, attribution, and non-endorsement statement are recorded in `NOTICE_XBRL_GL.md`. Other third-party material retains its own terms.
