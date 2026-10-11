# Full HMD Tavi v3 — Arelle acceptance

RESULT = PASS

## Drive authority and COPY integrity

- XBRL_GL_Next_Tavi_AccountingEntries_v3.json; Drive ID 1av-3SFf1px0A7LljEVyBYv5XnGP-3Oz3; bytes 405277; Drive and local COPY SHA-256 c5a22efd355f3184a6b308f7e6a052621bae401f955c619df8f5c783804db5b1.
- TAVI_ACCOUNTING_ENTRIES_MANIFEST_v3.json; Drive ID 1jYyE35k5d_V_nkyqwNjhTwL8H8QemieZ; bytes 17604; Drive and local COPY SHA-256 487c6edc696a85297f92a02edeb7fa9e7e5aaa7911738121590bcb9a77ccfa03.
- REVIEW_REPORT_v3.md; Drive ID 1qDhVznamyUn2kxw7jnp8qfh-I8rOz5QQ; bytes 2094; Drive and local COPY SHA-256 4f3f9b848cf50448c776ab54092f4732b73e3612eb5a0c9e9e6a594f379ae550.

Taxonomy path: tavi-poc/taxonomy/XBRL_GL_Next_Tavi_AccountingEntries_v3.json
Arelle branch: work/oim-taxonomy-tavi
Arelle HEAD: f8f50ee1d06a12f2e9798437c66e2d360514d6be
Validation timestamp: 2026-10-11T09:47:56.320760+09:00

Execution command (normal CLI entry; existing Arelle venv):

```text
/Users/pontsoleil/GitHub/Arelle/.venv/bin/python -B /Users/pontsoleil/GitHub/WORK/XBRL_GL_Next/docs/Codex/2026/202610/20261011/20261011_0946/full-hmd-tavi-v3-validation/scripts/run_validation.py
CLI arguments: ["--file", "/Users/pontsoleil/GitHub/WORK/XBRL_GL_Next/tavi-poc/taxonomy/XBRL_GL_Next_Tavi_AccountingEntries_v3.json", "--plugins", "OimTaxonomy", "--validate", "--keepOpen", "--internetConnectivity", "offline", "--logFile", "/Users/pontsoleil/GitHub/WORK/XBRL_GL_Next/docs/Codex/2026/202610/20261011/20261011_0946/full-hmd-tavi-v3-validation/evidence/ARELLE_LOG.xml", "--xdgConfigHome", "/Users/pontsoleil/GitHub/WORK/XBRL_GL_Next/docs/Codex/2026/202610/20261011/20261011_0946/full-hmd-tavi-v3-validation/evidence/config"]
```

JSON Schema = PASS; native load = PASS; full DTS = PASS.
Concepts = 399; dataTypes = 353; dimensions = 44; domains = 45; cubes = 46; networks = 1; tableTemplates = 0.
Static unresolved concept datatype / datatype base / non-datatype references = 0/0/0.
Loaded unresolved QName / datatype / references = 0/0/0; duplicate named objects = 0.
Errors / warnings = 0/0; formal Arelle executions = 1; process exit = 0.
The completed Arelle log was checked; no NameError, validator bypass, production function replacement or monkey patch.

Existing tavi-poc files unchanged. v1/v2 retained. Arelle source unchanged. Canonical unchanged. Official GIT unchanged. No commit/push or canonical promotion. Instance, CSV and Table Template were not used.
