# ADR-0002: Provider/consumer integration by versioned release package

- Status: Proposed
- Date: 2026-07-24

## Context

Projects under the WORK directory contain independent LHM files, generators and
runtime paths. Referencing a sibling working tree directly would couple their
behavior to uncommitted changes and make historical results unreproducible.

## Decision

XBRL-GL-Next will publish versioned semantic-model and OIM-taxonomy packages.
Consumer projects pin a package version and maintain only their syntax-specific
bindings and adapters. Migration uses explicit crosswalks and shadow comparison.

## Consequences

- The provider needs manifests, hashes, compatibility reports and release tests.
- Consumers must stop treating local LHM row order or filenames as identifiers.
- Consumer-specific syntax bindings stay outside this repository.
- Breaking semantic changes require a new version and migration record.
- Local sibling paths are allowed only as an explicit development override.
