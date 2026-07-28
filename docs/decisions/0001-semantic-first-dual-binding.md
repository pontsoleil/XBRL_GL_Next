# ADR-0001: Semantic-first model with dual syntax bindings

- Status: Proposed
- Date: 2026-07-24

## Context

The existing XBRL GL taxonomy expresses important containment semantics through
XBRL 2.1 tuples. OIM and xBRL-CSV do not serialize tuples in the same way.
Directly converting XML structures into dimensions risks making syntax-specific
choices part of the business meaning.

## Decision

Maintain FSM, BSM and LHM as the authoritative semantic pipeline. Graph Walk
produces LHM. Select HMD as a message-level subset of LHM during binding, then
generate the XBRL 2.1 Tuple and OIM dimensional realizations as peer syntax
bindings. A single-root LHM is content-identical to that root's HMD.
Stable semantic IDs and paths are assigned before QName, tuple, cube or CSV
column names.

## Consequences

- Cross-syntax comparison becomes testable.
- Module and profile decisions must be expressed above the syntax layer.
- Generators and mapping tables become required release artifacts.
- Existing tuple paths require explicit reverse-engineering and migration maps.
- A syntax binding may omit an unsupported feature, but must report the loss.
