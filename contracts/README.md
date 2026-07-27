**English** | [日本語](README_ja.md)

# Integration contracts

This directory contains project-authored draft contracts for the boundary
between XBRL GL Next and consuming projects.

## Registered with this candidate

- `consumer-mapping-template.csv` is an empty schema-only template. A separate
  copy is completed for each consumer profile during migration.
- The template must not contain production transactions, personal data,
  credentials, confidential configuration, or local absolute paths.
- `source_file_sha256`, contract name/version, review status, reviewer role,
  and review time preserve migration provenance without requiring a person's
  name.

## Planned, not yet registered

- `release-manifest.schema.json` is planned but is not part of this
  registration candidate.
- A versioned provider release package and its machine-readable manifest are
  also planned. They must not be described as available until registered and
  validated.

These contracts are versioned. Adding optional fields is backward compatible;
changing field meaning or removing a required field is not.

The repository licence applies only to project-authored contract text and
templates. It does not relicense third-party source material, derived
taxonomies, consumer data, or external standards. Material with unresolved
rights is not accepted even in the Private repository.
