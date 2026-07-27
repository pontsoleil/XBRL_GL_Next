# Workspace integration

## Purpose and status

XBRL GL Next is intended to become the provider of versioned semantic-model
and OIM taxonomy packages. Other repositories are consumers. Consumer
repositories and their data are not part of this registration candidate.

The provider release package, release manifest, consumer adapters, and
production cutover described below are **planned** and **not yet registered**.
No consumer may depend on a path inside a developer's working tree.

## Observed candidate consumers

### UADC_PoC

Local investigation identified an EN 16931 invoice LHM and related OIM
generation as a candidate transaction-document migration pilot. This is an
observation about a separate consumer repository, not a claim of registration,
ownership, endorsement, or current compatibility.

### LedgerExplorer

Local investigation identified accounting, sales, and purchasing LHM profiles
as a candidate ledger/subledger migration pilot. This is also a separate
consumer repository and is not included in the provider package.

## Planned provider release contract

A future consumer will integrate a pinned, versioned package rather than a
sibling working-tree path. The following layout is illustrative and is not
currently registered:

```text
release/
  manifest.json
  model/
    semantic-model.csv
    profile-lhm.csv
  taxonomy/
    catalog.xml
    entrypoints.json
  mappings/
    tuple-to-semantic.csv
    consumer-to-semantic.csv
  examples/
  validation/
    report.json
```

The planned manifest will identify the semantic-model contract, profile,
namespace date, entry points, source commit, file hashes, compatibility level,
and validation status. A manifest schema must not be treated as available
until it is separately registered and validated.

## Stable integration keys

The current design evaluates the following keys:

1. `semantic_id` — syntax-neutral identity retained by the current draft
   contracts;
2. `semantic_path` — human-readable logical path within a profile;
3. `concept_qname` — syntax-binding output;
4. `legacy_identifier` — migration-only consumer identifier.

CSV column position, generated row sequence, a QName prefix, and a local
filesystem path are not semantic identities. The future treatment of
`semantic_id` remains subject to the approved semantic-model contract.

## Migration stages

### Stage A — Inventory and freeze

Record each consumer model, binding, configured package, generated taxonomy,
test command, and SHA-256 without changing consumer behavior.

### Stage B — Explicit crosswalk

Use
[`../contracts/consumer-mapping-template.csv`](../contracts/consumer-mapping-template.csv)
to classify each row as `equivalent`, `rename`, `move`, `split`, `merge`,
`extension`, `deprecated`, or `unmapped`. Do not use an unreviewed fuzzy match.

The committed template remains empty. Completed mappings may contain consumer
identifiers and therefore require a separate privacy, confidentiality,
licence, and sharing review before registration.

### Stage C — Shadow generation

Generate consumer output from both the pinned legacy package and the candidate
provider profile. Compare semantic facts, repeated-row scope, datatype, unit,
cardinality, and entry point.

### Stage D — Consumer adapter

Resolve a versioned provider package. A local package may be supplied for
development through an environment variable such as
`XBRL_GL_NEXT_PACKAGE`; production and CI must use a pinned package or fixture.

### Stage E — Cutover

Switch only after positive, negative, and round-trip tests pass. Retain a
pinned rollback package for at least one migration cycle.

### Stage F — Retirement

Retire a project-local model generator only after authority, ownership,
release, and rollback responsibilities have moved to the provider.
Consumer-specific syntax bindings remain in the consumer repository.

## Compatibility gates

- every legacy row has an explicit mapping disposition;
- semantic identity is not reused with a different definition;
- repeated-Class scope produces equivalent fact grouping;
- datatype, unit, nil behavior, and cardinality are equal or deliberately
  migrated;
- source round trips preserve all bound values;
- OIM metadata resolves a registered taxonomy entry point;
- an independent processor validates the package;
- consumer tests pass against a pinned provider version;
- the package and mapping contain no credentials, real transactions,
  unapproved personal data, or confidential configuration.

## Ownership, licence, and isolation

Project-authored text and empty templates may use the project documentation
licence. External models, standards, consumer files, and derived taxonomies
remain subject to their respective owners' terms and are not relicensed.
Unresolved-rights material is not registered even in the Private repository.

The provider never writes directly into a consumer repository. Repository
roles, environment variables, and repository-relative paths replace
developer-specific Windows paths.
