# ADR-0007: FSM_q column contract, Association identity, and root-specific HMD

- Status: Accepted
- Date: 2026-07-29
- Scope: Current PoC implementation contract

## Context

The former PoC contract combined Association role text with
`property_term`, resulting in a 14-column FSM and 15-column BSM. The reviewed
`FSM_q.xlsx` contract separates those meanings. LHM and HMD generation also
need an unambiguous distinction between a combined domain hierarchy and a
single-root message hierarchy.

`Accepted` records a technical design decision only. It does not mean that
Part 1 or any project artifact has been formally approved by a participating
organisation.

## Decision

1. FSM has 15 columns:
   `sequence`, `level`, `property_type`, `identifier`, `module`, `class_term`,
   `property_term`, `association_role`, `representation_term`,
   `associated_module`, `associated_class`, `multiplicity`, `definition`,
   `label_local`, `definition_local`.
2. BSM has the same 15 columns followed by `id`, for 16 columns total.
3. BSM has no `element` column.
4. LHM and HMD use the same 17-column header:
   `sequence`, `module`, `level`, `type`, `identifier`, `name`, `datatype`,
   `multiplicity`, `domain_name`, `definition`, `label_local`,
   `definition_local`, `element`, `id`, `semantic_path`, `associated_module`,
   `class_term`.
5. Attribute identity is `property_term`.
6. Association identity is
   `(association_role, associated_module, associated_class)`.
   `property_term`, Association kind, representation term, and multiplicity
   are not part of Association identity.
7. Graph Walk over the declared root Class set produces the combined LHM.
8. Graph Walk from one explicitly supplied root Class QName produces the
   root-specific HMD directly from BSM. An LHM need not be generated first.
9. HMD is not a fourth semantic model.
10. A Reference Association emits its R occurrence and target PK Attributes as
    `REF`. If no PK exists, no row is emitted below R, a non-fatal diagnostic is
    recorded, and processing continues.
11. The reviewed FSM input removes the redundant
    `cor:Entity_ Party / Business Description` declaration inherited from
    `cor:Party`, while retaining `Party Business Description`. The full
    Accounting Entries and Business Transactions root set must complete Graph
    Walk without an element collision.

## Consequences

- Legacy 14-column FSM and 15-column BSM headers are rejected as current input.
- Header order, missing columns, extra columns, and duplicate columns are
  input errors rather than targets for silent correction.
- CLI help, documentation, fixtures, and tests must distinguish a one-root HMD
  from a multiple-root combined LHM.
- The reviewed full-data fixture is a required regression input for multiple-root
  element naming and must not be replaced by a reduced synthetic collision case.
- ADR-0006 remains a historical design record. This ADR supersedes ADR-0006
  where its column counts, Association identity, or HMD derivation conflict
  with this decision.
